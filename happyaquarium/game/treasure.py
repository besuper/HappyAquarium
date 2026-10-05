import random
from datetime import datetime, timedelta, timezone

from . import catalog, pollution


def is_chest(row):
    item = catalog.ITEMS.get(row["itemId"])
    return bool(item) and item["item_type"] == catalog.ITEM_TYPE_CHEST


def last_reset(now, config):
    hour = config["daily_treasure"]["reset_utc_hour"]
    current = datetime.fromtimestamp(now, timezone.utc)
    reset = current.replace(hour=hour, minute=0, second=0, microsecond=0)
    if reset > current:
        reset -= timedelta(days=1)
    return int(reset.timestamp())


def has_coins(row, now, config):
    return row.get("last_coin_collect", 0) < last_reset(now, config)


def payout(tank, now, config):
    settings = config["daily_treasure"]
    cleanliness = 1 - pollution.current(tank, now, config) / pollution.MAX_POLLUTION
    fish = [row for row in tank["items"] if not is_chest(row)]
    fullness = 1 - sum(row["hunger"] for row in fish) / (100 * len(fish)) if fish else 1
    bonus = (cleanliness + fullness) / 2
    low, high = settings["min_coins"], settings["max_coins"]
    return round(low + (high - low) * bonus * random.uniform(0.5, 1))
