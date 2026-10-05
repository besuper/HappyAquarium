import json
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_FILE = Path(os.environ.get("HA_CONFIG", PROJECT_ROOT / "config.json"))


def load(path=CONFIG_FILE):
    config = json.loads(Path(path).read_text(encoding="utf-8"))
    server = config["server"]
    for key in ("assets_dir", "players_dir"):
        server[key] = (PROJECT_ROOT / server[key]).resolve()
    return config


CONFIG = load()
