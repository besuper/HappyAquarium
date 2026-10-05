import json
from pathlib import Path
from urllib.parse import urlsplit

from ..config import CONFIG

PLATFORM = {
    "achievementsActive": False,
    "activeFBCred": False,
    "activeFBFunc": False,
    "altTankLoadingMethodActive": False,
    "blankNeighboursTabsActive": True,
    "collectionsActive": False,
    "earnCreditsActive": False,
    "epicTanksActive": False,
    "expeditionsActive": False,
    "fbTextActive": False,
    "frogsActive": False,
    "fullScreenActive": True,
    "gamebarActive": False,
    "getMoreCreditsActive": False,
    "getMoreUrl": "",
    "getNewGetMorePopupActive": False,
    "goldenTicketActive": False,
    "hybridTutorialActive": False,
    "hybridsActive": False,
    "lockBoxActive": False,
    "lotteryActive": False,
    "midwayGameActive": False,
    "playspanIsActive": False,
    "protocols": {},
    "saleOfTheDayActive": False,
    "spinAndWinActive": False,
    "superFishClubActive": False,
    "textFieldsActive": True,
    "trainFishActive": False,
    "trainFishAgainActive": False,
    "treasureHuntActive": False,
    "trialpayActive": False,
    "videoAdsEnabled": False,
    "voteActive": False,
    "whaleFeaturesActive": False,
    "zapayaAdsEnabled": False,
}

STORE_TYPE_ITEM = 0
STORE_TYPE_FOOD = 22
STORE_TYPE_GENERIC = 17
STORE_FLAG_NOT_IN_STORE = 1 << 4
ITEM_TYPE_CHEST = 5
TANK_ID_STORAGE = 100000
SLOT_INBOX = 1000000

# Hardcoded in the client (UI_Main.feedRegular / feedSuper)
FOOD_REGULAR = 1
FOOD_SUPER = 7
FOOD_TYPES = {
    FOOD_REGULAR: {"foodTypeId": FOOD_REGULAR, "title": "Fish Food", "description": "", "artUrl": ""},
    FOOD_SUPER: {"foodTypeId": FOOD_SUPER, "title": "Super Food", "description": "", "artUrl": ""},
}

CATALOGUE_FILE = Path(__file__).parent / "data" / "crowdstar_store_2010-03-05.json"
_CATALOGUE = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8"))

MALE_NAMES = _CATALOGUE["maleNames"]
FEMALE_NAMES = _CATALOGUE["femaleNames"]


def art_path(url):
    return urlsplit(url).path.lstrip("/") if url else ""


def has_art(path):
    return bool(path) and (CONFIG["server"]["assets_dir"] / path).is_file()


def convert_item(raw):
    art = art_path(raw["artUrl"])
    baby = art_path(raw.get("babyArtUrl"))
    item_id = int(raw["itemId"])
    return {
        "item_id": item_id,
        "item_type": int(raw["itemType"]),
        "title": raw["title"],
        "title_english": raw["title_english"],
        "description": raw["description"].strip(),
        "art_url": art,
        "baby_art_url": baby if has_art(baby) else art,
        "alt_art_url": "",
        "scale_factor": float(raw["scaleFactor"]),
        "alt_scale_factor": float(raw["scaleFactor"]),
        "base_speed": int(raw["baseSpeed"]),
        "coin_cost": int(raw["coinCost"]),
        "action_point_cost": int(raw["actionPointCost"]),
        "cost_mate_action_points": 0,
        "population_required": int(raw["populationRequired"]),
        "level_required": int(raw["levelRequired"]),
        "pollution_caused": int(raw["pollutionCaused"]),
        "food_required": int(raw["foodRequired"]),
        "food_frequency": int(raw["foodFrequency"]),
        "growth_rate": int(raw["growthRate"]),
        "feed_image": raw.get("feedImage", ""),
        "movement_type": int(raw["movementType"]),
        "abilities": int(raw["abilities"]),
        "should_preload": 1,
        "frame_id": 0,
        "animated": int(raw["animated"]),
        "life_span": 0,
        "charges": 0,
        "provides_coins": int(raw["providesCoins"]),
        "giftable": int(raw["giftable"]),
        "breeds_with_item_ids": sorted({int(i) for i in raw["breedsWithItemIds"]}),
        "flags": 0,
        "force_gender": 0,
    }


ALL_ITEMS = {row["item_id"]: row for row in map(convert_item, _CATALOGUE["items"].values())}
RECOVERED = {item_id for item_id, row in ALL_ITEMS.items() if has_art(row["art_url"])}


def with_placeholder(row, art):
    return {**row, "art_url": art, "baby_art_url": art}


# Items the game cannot work without (the daily chest) get stub art; they are not sold.
PLACEHOLDERS = {int(k): v for k, v in CONFIG["placeholder_art"].items()}
ITEMS = {item_id: ALL_ITEMS[item_id] for item_id in RECOVERED}
ITEMS.update({item_id: with_placeholder(ALL_ITEMS[item_id], art)
              for item_id, art in PLACEHOLDERS.items() if item_id not in RECOVERED})
STORE_ROWS = {int(row["storeItemId"]): row for row in _CATALOGUE["storeItems"] if int(row["itemId"]) in RECOVERED}
STORE = {store_id: int(row["itemId"]) for store_id, row in STORE_ROWS.items()}

# NewStore.filterItems() forces the item titled exactly "Clownfish" into slot 1 of the fish tab;
# with a single fish on sale slot 0 stays null and the store crashes while sorting.
if sum(1 for item_id in STORE.values() if ITEMS[item_id]["item_type"] == 1) < 2:
    for item in ITEMS.values():
        if item["title"] == "Clownfish":
            item["title"] += " "


FOOD_ITEM_TYPES = {1: FOOD_REGULAR, 2: FOOD_SUPER}
FOOD_STORE_ID_OFFSET = 10000


def convert_store_food(raw):
    amount = int(raw["amount"])
    return {
        "food_item_id": int(raw["storeFoodId"]),
        "item_type": 1,
        "coin_cost": int(raw["coinCost"]),
        "action_point_cost": int(raw["actionPointCost"]),
        "food_amount": amount,
        "icon_frame": 1,
        "level_required": 1,
        "title": f"{amount} Fish Food",
        "description": "Shakes of food for all fish.",
        "feed_image": "",
        "flags": 0,
        "active": 1,
        "related_item_id": 0,
    }


FOOD_ITEMS = {
    int(raw["storeFoodId"]): convert_store_food(raw)
    for raw in _CATALOGUE["storeFoods"] if int(raw["foodTypeId"]) == FOOD_REGULAR
}
FOOD_STORE = {FOOD_STORE_ID_OFFSET + food_id: food_id for food_id in FOOD_ITEMS}


# DailyTreasure needs a daily-treasure GenericItem and its store row for the "play again" button
DAILY_TREASURE_ID = 1
DAILY_TREASURE_STORE_ID = 20000


def generic_items():
    return {str(DAILY_TREASURE_ID): {
        "generic_item_id": DAILY_TREASURE_ID,
        "item_type": 4,
        "coin_cost": 0,
        "action_point_cost": CONFIG["daily_treasure"]["replay_pearls"],
        "art_url": "",
        "level_required": 1,
        "title": "Daily Treasure",
        "description": "",
        "feed_image": "",
        "flags": 0,
        "meta_info": "",
        "start_time": 0,
        "end_time": 0,
        "active": 1,
    }}


TANKS = {
    1: {
        "tank_id": 1,
        "title": "50 Gallon Tank",
        "description": "Starter tank",
        "population_limit": 20,
        "coin_cost": 0,
        "action_point_cost": 0,
        "beauty_points": 0,
        "level_required": 1,
        "pollution_index": 1,
        "scale_factor": 1,
        "art_url": "swf/tank/Tank_Stub.swf",
        "gravel_art_url": "",
        "dirt_art_url": "swf/tank/Tank_Stub_Dirt.swf",
        "lock_type": 0,
        "lock_value": 0,
        "flags": 0,
        "width": 760,
        "height": 520,
    }
}

# The inbox (gifts, inventory) is a UserTank in slot 1000000 using a storage tank; the
# client never loads art for tank ids >= 100000.
TANKS[TANK_ID_STORAGE] = {**TANKS[1], "tank_id": TANK_ID_STORAGE, "title": "Inbox", "description": "",
                          "art_url": "", "dirt_art_url": "", "population_limit": 1000}

GRAVEL = {
    1: {
        "gravel_id": 1,
        "title": "Sand",
        "description": "",
        "frame_num": 1,
        "invite_cost": 0,
        "coin_cost": 0,
        "action_point_cost": 0,
        # The client loads swf/tank/<art_url>{50,100,150,Small,Medium,Large}.swf
        "art_url": "Gravel_Stub",
        "animated": 0,
        "flags": 0,
    }
}

WALLPAPERS = {
    0: {
        "wallpaper_id": 0,
        "title": "None",
        "description": "",
        "thumb_url": "",
        "img_url": "",
        "invite_cost": 0,
        "coin_cost": 0,
        "actionpoint_cost": 0,
        "sunlight": "SunLight.png",
        "alpha": 1,
        "flags": 0,
        "in_store": 0,
    }
}


def absolute(row, cdn, *keys):
    row = dict(row)
    for key in keys:
        if row.get(key):
            row[key] = cdn + row[key]
    return row


def items(cdn):
    return {str(i): absolute(row, cdn, "art_url", "baby_art_url") for i, row in ITEMS.items()}


def tanks(cdn):
    return {str(i): absolute(row, cdn, "art_url", "dirt_art_url") for i, row in TANKS.items()}


def food_items():
    return {str(i): row for i, row in FOOD_ITEMS.items()}


def store_items():
    rows = {}
    for store_id, item_id in STORE.items():
        raw = STORE_ROWS[store_id]
        rows[str(store_id)] = store_row(store_id, item_id, STORE_TYPE_ITEM, ITEMS[item_id]["level_required"], raw)
    for store_id, food_id in FOOD_STORE.items():
        rows[str(store_id)] = store_row(store_id, food_id, STORE_TYPE_FOOD, food_id)
    # DailyTreasure looks its store row up by GenericItem.genericItemId, which is 17 * 100000 + id
    rows[str(DAILY_TREASURE_STORE_ID)] = {
        **store_row(DAILY_TREASURE_STORE_ID, DAILY_TREASURE_ID, STORE_TYPE_GENERIC, 0, flags=STORE_FLAG_NOT_IN_STORE),
        "item_id": STORE_TYPE_GENERIC * 100000 + DAILY_TREASURE_ID,
    }
    return rows


def store_row(store_id, table_id, store_type, priority, raw=None, flags=0):
    raw = raw or {}
    return {
        "store_item_id": store_id,
        "id": table_id,
        "item_id": table_id,
        "item_type": store_type,
        "sex": int(raw.get("sex", 0)),
        "age": int(raw.get("age", 0)),
        "status": int(raw.get("status", 0)),
        "animated": int(raw.get("animated", 0)),
        "flags": flags,
        "category_priority": priority,
        "special_priority": 0,
        "cost_override": int(raw.get("costOverride", 0)),
        "cost_override_coins": int(raw.get("costOverrideCoins", 0)),
        "cost_override_action_points": int(raw.get("costOverrideActionPoints", 0)),
        "is_on_sale": 0,
        "is_new": 0,
        "date_end": 0,
        "sale_date_start": 0,
        "sale_date_end": 0,
        "date_created": 0,
        "bulk_quantity": 1,
        "lock_type": 0,
        "lock_value": 0,
        "offset_x": 0,
        "offset_y": 0,
    }
