import json
import time

from . import action
from ._common import OK

MAX_XP_PER_FEEDING = 500


@action("feed_fish")
def feed_fish(ctx):
    player = ctx.player
    now = int(time.time())
    items = {row["tankItemId"]: row for tank in player["tanks"] for row in tank["items"]}
    for fed in json.loads(ctx.params.get("fish_json") or "[]"):
        row = items.get(fed.get("tankItemId"))
        if row is None:
            continue
        row["hunger"] = max(0, min(100, int(fed.get("hunger", row["hunger"]))))
        row["last_hunger_update"] = now
        for key in ("xLocation", "yLocation", "zLocation"):
            if key in fed:
                row[key] = fed[key]
        row["flipped"] = 1 if fed.get("flipped") else 0

    for food in json.loads(ctx.params.get("user_foods_json") or "[]"):
        key = str(food.get("foodTypeId"))
        if key in player["foods"]:
            player["foods"][key] = max(0, min(player["foods"][key], int(food.get("amount", 0))))

    client_xp = int(json.loads(ctx.params.get("player_json") or "{}").get("xp") or 0)
    if player["xp"] < client_xp <= player["xp"] + MAX_XP_PER_FEEDING:
        player["xp"] = client_xp
    return OK
