import math

from . import catalog

MAX_POLLUTION = 100000
SECONDS_TO_MAX_DIRTY = 2 * 24 * 3600
POLLUTION_PER_SCRUB = 10000


def ratio(tank):
    total = 0
    for row in tank["items"]:
        item = catalog.ITEMS.get(row["itemId"])
        if item and item["pollution_caused"] > 0:
            total += item["pollution_caused"]
    return total / catalog.TANKS[tank["tank_id"]]["pollution_index"]


def current(tank, now):
    elapsed = max(0, now - tank.get("last_pollution_update", now))
    added = math.ceil(MAX_POLLUTION * elapsed / SECONDS_TO_MAX_DIRTY * ratio(tank))
    return min(MAX_POLLUTION, tank["pollution"] + added)
