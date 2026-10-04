"""Game catalogue sent in get_init_data.

Items come from the original 2010 CrowdStar catalogue; tanks, gravel and wallpapers are
stubs (none were archived). Field names follow the parseFromJSON methods of the
decompiled client (crowdstar.aquarium.data.*).
"""
import json
from pathlib import Path
from urllib.parse import urlsplit

from ..config import Config

# Feature flags read through Game.getPlatformProperty(); a missing key crashes the
# client (#1069), so every key is listed. Features without server support are off.
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

STORE_TYPE_ITEM = 0  # StoreItem.TYPE_ITEM

# Food type ids hardcoded in the client (UI_Main.feedRegular / feedSuper)
FOOD_REGULAR = 1
FOOD_SUPER = 7
FOOD_TYPES = {
    FOOD_REGULAR: {"foodTypeId": FOOD_REGULAR, "title": "Fish Food", "description": "", "artUrl": ""},
    FOOD_SUPER: {"foodTypeId": FOOD_SUPER, "title": "Super Food", "description": "", "artUrl": ""},
}
# Shakes given to new players (one shake = one click with the feed cursor)
STARTING_FOOD = {FOOD_REGULAR: 100, FOOD_SUPER: 10}

CATALOGUE_FILE = Path(__file__).parent / "data" / "crowdstar_store_2010-03-05.json"
_CATALOGUE = json.loads(CATALOGUE_FILE.read_text(encoding="utf-8"))

STARTER_FISH = 6  # Clownfish
MALE_NAMES = _CATALOGUE["maleNames"]
FEMALE_NAMES = _CATALOGUE["femaleNames"]


def art_path(url):
    """'http://cdnaquarium.crowdstar.com/swf/fish/X.swf?v=12' -> 'swf/fish/X.swf'"""
    return urlsplit(url).path.lstrip("/") if url else ""


def has_art(path):
    return bool(path) and (Config.ASSETS_DIR / path).is_file()


def convert_item(raw):
    """2010 catalogue row -> Item.parseFromJSON row (art paths relative to the CDN root)."""
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
        "action_point_cost": int(raw["actionPointCost"]),  # pearls
        "cost_mate_action_points": 0,
        "population_required": int(raw["populationRequired"]),
        "level_required": int(raw["levelRequired"]),
        "pollution_caused": int(raw["pollutionCaused"]),
        "food_required": int(raw["foodRequired"]),  # flakes to go from starving to full
        "food_frequency": int(raw["foodFrequency"]),  # seconds from full to starving
        "growth_rate": int(raw["growthRate"]),  # seconds to grow up
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
ITEMS = {item_id: row for item_id, row in ALL_ITEMS.items() if has_art(row["art_url"])}
STORE_ROWS = {int(row["storeItemId"]): row for row in _CATALOGUE["storeItems"] if int(row["itemId"]) in ITEMS}
# store_item_id -> item_id
STORE = {store_id: int(row["itemId"]) for store_id, row in STORE_ROWS.items()}

# NewStore.filterItems() forces the item titled exactly "Clownfish" into slot 1 of the fish
# tab (itemList[1] = clownFish). With a single fish on sale, slot 0 becomes null and the
# store crashes while sorting. Until more fish art is recovered, dodge the exact match.
if sum(1 for item_id in STORE.values() if ITEMS[item_id]["item_type"] == 1) < 2:
    for item in ITEMS.values():
        if item["title"] == "Clownfish":
            item["title"] += " "


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
    """Copy of `row` with the given relative art paths prefixed by the CDN URL."""
    row = dict(row)
    for key in keys:
        if row.get(key):
            row[key] = cdn + row[key]
    return row


def items(cdn):
    return {str(i): absolute(row, cdn, "art_url", "baby_art_url") for i, row in ITEMS.items()}


def tanks(cdn):
    return {str(i): absolute(row, cdn, "art_url", "dirt_art_url") for i, row in TANKS.items()}


def store_items():
    """StoreItem rows (StoreItem.parseFromJSON) for everything in STORE."""
    rows = {}
    for store_id, item_id in STORE.items():
        raw = STORE_ROWS[store_id]
        rows[str(store_id)] = {
            "store_item_id": store_id,
            "id": item_id,
            "item_id": item_id,
            "item_type": STORE_TYPE_ITEM,
            "sex": int(raw["sex"]),
            "age": int(raw["age"]),
            "status": int(raw["status"]),
            "animated": int(raw["animated"]),
            "flags": 0,
            "category_priority": ITEMS[item_id]["level_required"],
            "special_priority": 0,
            "cost_override": int(raw["costOverride"]),
            "cost_override_coins": int(raw["costOverrideCoins"]),
            "cost_override_action_points": int(raw["costOverrideActionPoints"]),
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
    return rows
