import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

class Config:
    ASSETS_DIR = Path(os.environ.get("HA_ASSETS_DIR", PROJECT_ROOT / "assets"))
    PLAYERS_DIR = Path(os.environ.get("HA_PLAYERS_DIR", PROJECT_ROOT / "data" / "players"))
    DEFAULT_USER = os.environ.get("HA_DEFAULT_USER", "player")
    RUFFLE_URL = os.environ.get("HA_RUFFLE_URL", "https://unpkg.com/@ruffle-rs/ruffle")
    FLASH_LOG = os.environ.get("HA_FLASH_LOG", "1") == "1"
