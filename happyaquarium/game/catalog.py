"""Static game catalogue sent in get_init_data.

The real catalogue lived on CrowdStar's/101XP's servers and was never archived, so
only items whose art survived (or a stub) are listed here. Field names follow the
parseFromJSON methods of the decompiled client (crowdstar.aquarium.data.*).
"""

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

ITEM_TYPE_FISH = 1  # Item.ITEM_TYPE_FISH
STORE_TYPE_ITEM = 0  # StoreItem.TYPE_ITEM


def fish(item_id, title, art, coins=0, pearls=0, level=1, description=""):
    """An Item row (Item.parseFromJSON). `art` is relative to the CDN root."""
    return {
        "item_id": item_id,
        "item_type": ITEM_TYPE_FISH,
        "title": title,
        "title_english": title,
        "description": description,
        "art_url": art,
        "baby_art_url": art,
        "alt_art_url": "",
        "scale_factor": 1,
        "alt_scale_factor": 1,
        "base_speed": 1,
        "coin_cost": coins,
        "action_point_cost": pearls,  # pearls are called "action points" in the client
        "cost_mate_action_points": 0,
        "population_required": 1,
        "level_required": level,
        "pollution_caused": 1,
        "food_required": 1,
        "food_frequency": 1,
        "growth_rate": 1,
        "movement_type": 1,
        "should_preload": 1,
        "frame_id": 0,
        "animated": 0,
        "life_span": 0,
        "charges": 0,
        "provides_coins": 1,
        "giftable": 1,
        "breeds_with_item_ids": [item_id],
        "flags": 0,
        "force_gender": 0,
    }


ITEMS = {
    1: fish(1, "Three Stripe Clownfish", "swf/fish/AQ_Fish_01_ClownFishThreeStripe.swf", coins=16,
            description="Flexy body allows this fish to get around quickly and avoid danger."),
}

# store_item_id -> item_id
STORE = {1: 1}

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
        rows[str(store_id)] = {
            "store_item_id": store_id,
            "id": item_id,
            "item_id": item_id,
            "item_type": STORE_TYPE_ITEM,
            "sex": 0,
            "age": 0,
            "status": 1,
            "animated": 0,
            "flags": 0,
            "category_priority": ITEMS[item_id]["level_required"],
            "special_priority": 0,
            "cost_override": 0,
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
