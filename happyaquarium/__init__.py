import json
import logging
import re

from flask import Flask, Response, abort, render_template, request, send_from_directory

from .config import Config
from .game import actions, init_data
from .storage import PlayerStore, app_user_id, valid_user
from .swf import SILENT_MP3, patched_main_swf

log = logging.getLogger("happyaquarium")

MAIN_SWF = "main_deploy_preloaded.swf"
CROSSDOMAIN = """<?xml version="1.0"?>
<cross-domain-policy><allow-access-from domain="*"/></cross-domain-policy>"""


class CollapseSlashes:
    """WSGI middleware: '/assets////swf/x' -> '/assets/swf/x' (see swf.LOCAL_CDN)."""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ["PATH_INFO"] = re.sub(r"/{2,}", "/", environ.get("PATH_INFO", ""))
        return self.app(environ, start_response)


def json_reply(data):
    # No spaces: the client looks for the literal substring "error":0
    return Response(json.dumps(data, separators=(",", ":")), mimetype="application/json")


def create_app(config=Config):
    app = Flask(__name__)
    app.config.from_object(config)
    app.wsgi_app = CollapseSlashes(app.wsgi_app)
    assets_dir = app.config["ASSETS_DIR"]
    players = PlayerStore(app.config["PLAYERS_DIR"])

    def cdn_url():
        return request.host_url + "assets/"

    @app.get("/")
    def play():
        user = request.args.get("user", app.config["DEFAULT_USER"])
        if not valid_user(user):
            abort(400, "user must be 1-32 characters: letters, digits, _ or -")
        players.load(user)  # create the save on first visit
        flashvars = {
            "swf_to_load": cdn_url() + MAIN_SWF,
            "img_to_load": cdn_url() + "img/loading.png",
            "version": "1",
            "tip_to_display": "",
            "cdn_url": cdn_url(),
            "callback_url": request.host_url.rstrip("/"),
            "app_url": request.host_url,
            "user_id": user,
            "app_user_id": str(app_user_id(user)),
            "app_id": "134920244184",  # Happy Aquarium's Facebook app id
            "network": "0",  # Transport.NETWORK_FACEBOOK
            "language": "en",
            "language_file": "",
            "fb_sig_locale": "en_US",
            "mobile": "0",
            "signed_request": "",
            "user_prefs": "0",
        }
        return render_template("play.html", flashvars=flashvars, ruffle_url=app.config["RUFFLE_URL"],
                               flash_log=app.config["FLASH_LOG"], user=user)

    @app.get("/assets/<path:path>")
    @app.get("/swf/<path:path>", defaults={"prefix": "swf/"})
    def assets(path, prefix=""):
        # Sounds are requested from callback_url (/swf/...) because Transport.useCDN is off.
        path = prefix + path
        if path == MAIN_SWF:
            swf_path = assets_dir / MAIN_SWF
            return Response(patched_main_swf(swf_path, swf_path.stat().st_mtime),
                            mimetype="application/x-shockwave-flash")
        if (assets_dir / path).is_file():
            return send_from_directory(assets_dir, path)
        if path.startswith("swf/sound/") and path.endswith(".mp3"):
            return Response(SILENT_MP3, mimetype="audio/mpeg")  # sound effects were never recovered
        log.info("missing asset: %s", path)
        abort(404)

    @app.get("/crossdomain.xml")
    def crossdomain():
        return Response(CROSSDOMAIN, mimetype="text/xml")

    @app.route("/comm/<action>.php", methods=["GET", "POST"])
    def comm(action):
        params = request.values.to_dict()
        user = params.get("user_id", "")
        if not valid_user(user):
            return json_reply({"error": 403})
        player = players.load(user)

        if action == "get_init_data":
            return json_reply(init_data.build(player, cdn_url()))
        if action in actions.STATIC_REPLIES:
            return json_reply(actions.STATIC_REPLIES[action])
        handler = actions.HANDLERS.get(action)
        if handler is None:
            log.warning("unhandled comm call %s %s", action, {k: v[:80] for k, v in params.items()})
            return json_reply({"error": 0})
        reply = handler(player, params)
        players.save(player)
        log.info("comm %s -> error=%s", action, reply.get("error"))
        return json_reply(reply)

    @app.post("/debug/flash-log")
    def flash_log():
        if app.config["FLASH_LOG"]:
            log.info("[flash] %s", request.get_data(as_text=True).strip())
        return "", 204

    return app
