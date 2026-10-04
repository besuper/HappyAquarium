import json
import os
import re
import threading
import time
import zlib
from pathlib import Path

from .game.catalog import STARTER_FISH
from .game.catalog import STARTING_FOOD as _STARTING_FOOD

SAVE_VERSION = 1
STARTING_FOOD = {str(k): v for k, v in _STARTING_FOOD.items()}
USER_RE = re.compile(r"^[A-Za-z0-9_-]{1,32}$")

_lock = threading.Lock()


def valid_user(user_id: str) -> bool:
    return bool(USER_RE.match(user_id or ""))


def app_user_id(user_id: str) -> int:
    """Stable numeric id for the client's app_user_id fields."""
    return zlib.crc32(user_id.encode()) % 1_000_000_000 + 1


def new_tank_item(tank_item_id, item_id, name, user_tank_id=1, sex=1, age=100, x=380, y=250):
    now = int(time.time())
    return {
        "tankItemId": tank_item_id,
        "userTankId": user_tank_id,
        "itemId": item_id,
        "name": name,
        "sex": sex,
        "hunger": 50,  # 0 = full, 100 = starving
        "mood": 100,
        "status": 1,
        "dateCreated": now,
        "age": age,
        "xLocation": x,
        "yLocation": y,
        "zLocation": 0,
        "sicknessLevel": 0,
        "dirtSicknessLevel": 0,
        "canBreed": 1,
        "trickLevel": 0,
        "canTrain": 0,
        "isGift": 0,
        "giftGiver": 0,
        "last_hunger_update": now,
        "last_age_update": now,
        "sellAmount": 10,
        "sparkle": 0,
        "userScale": 100,
        "hasCoins": 0,
        "flipped": 0,
    }


def new_player(user_id: str) -> dict:
    return {
        "version": SAVE_VERSION,
        "user_id": user_id,
        "name": user_id,
        "created": int(time.time()),
        "coins": 5000,
        "pearls": 50,
        "xp": 1,
        "foods": dict(STARTING_FOOD),
        # flashAppUserMetaData, written by the client through comm/set_key.php.
        # "ts" is the tutorial step; its "Get My Fish" step needs the original store, so skip it.
        "meta": {"ts": "tutorialComplete"},
        "next_tank_item_id": 2,
        "tanks": [
            {
                "user_tank_id": 1,
                "tank_id": 1,
                "slot": 0,
                "title": "My Aquarium",
                "gravel_id": 1,
                "tank_bg_id": 0,
                "lighting_id": 0,
                "pollution": 0,
                "items": [new_tank_item(1, STARTER_FISH, "Nemo")],
            }
        ],
    }


class PlayerStore:
    def __init__(self, directory: Path):
        self.directory = Path(directory)

    def _path(self, user_id: str) -> Path:
        if not valid_user(user_id):
            raise ValueError(f"invalid user id {user_id!r}")
        return self.directory / f"{user_id}.json"

    def load(self, user_id: str) -> dict:
        """Return the player's save, creating it on first visit."""
        path = self._path(user_id)
        with _lock:
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        player = new_player(user_id)
        self.save(player)
        return player

    def save(self, player: dict) -> None:
        path = self._path(player["user_id"])
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(".json.tmp")
        with _lock:
            tmp.write_text(json.dumps(player, indent=2), encoding="utf-8")
            os.replace(tmp, path)  # atomic: never leaves a half-written save
