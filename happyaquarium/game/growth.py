from . import catalog

GROWING_TYPES = {1, 14, 18}
MAX_HUNGER_TO_GROW = 99

EGG = -2
NONE = -1
ADULT = 4


def grows(item):
    return bool(item) and item["item_type"] in GROWING_TYPES and item["growth_rate"] > 0


def current_age(row, now):
    item = catalog.ITEMS.get(row["itemId"])

    if not grows(item) or row["age"] < 0:
        return row["age"]

    elapsed = max(0, now - row.get("last_age_update", now))

    if item["food_frequency"] > 0:
        until_too_hungry = (MAX_HUNGER_TO_GROW - row["hunger"]) * item["food_frequency"] / 100
        elapsed = min(elapsed, max(0, until_too_hungry))

    return row["age"] + int(elapsed)


def level(row, now):
    item = catalog.ITEMS.get(row["itemId"])

    if not grows(item):
        return NONE

    age = current_age(row, now)

    if age < 0:
        return EGG
        
    return min(ADULT, age // item["growth_rate"])


def settle(row, now):
    row["age"] = current_age(row, now)
    row["last_age_update"] = now
