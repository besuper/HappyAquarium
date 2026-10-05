import json
import math
import time

from . import action
from ._common import find_tank
from ..game import levels, pollution


@action("update_user_tank")
def update_user_tank(ctx):
    player = ctx.player
    data = json.loads(ctx.params.get("user_tank") or "{}")
    tank = find_tank(player, int(data.get("userTankId", 0)))
    now = int(time.time())

    before = pollution.current(tank, now)
    after = max(0, min(before, int(data.get("currentPollution", before))))
    tank["pollution"] = after
    tank["last_pollution_update"] = now

    scrubs = math.ceil((before - after) / pollution.POLLUTION_PER_SCRUB)
    player["xp"] += scrubs * levels.xp_for_scrub(player["xp"])
    return {"error": 0, "xp": player["xp"]}
