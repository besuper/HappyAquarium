import time

from . import action
from ..game import catalog, growth, pollution, treasure
from ..storage import app_user_id

def current_hunger(tank_item, now):
    # Hunger is inverted: 0 = full, 100 = starving. Crawlers have food_frequency 0 and never get hungry.
    item = catalog.ITEMS.get(tank_item["itemId"])
    frequency = item["food_frequency"] if item else 0
    
    if frequency <= 0:
        return tank_item["hunger"]

    elapsed = max(0, now - tank_item.get("last_hunger_update", now))

    return min(100, tank_item["hunger"] + elapsed * 100 // frequency)


def tank_item(row, now, config):
    row = {**row, "hunger": current_hunger(row, now), "last_hunger_update": now,
           "age": growth.current_age(row, now), "last_age_update": now}

    if treasure.is_chest(row):
        row["hasCoins"] = int(treasure.has_coins(row, now, config))

    return row


def tank_items(tank, now, config):
    return [tank_item(row, now, config) for row in tank["items"]]


def user_tank(player, tank, app_id, now, config):
    return {
        "user_id": player["user_id"],
        "user_tank_id": tank["user_tank_id"],
        "tank_id": tank["tank_id"],
        "is_loaded": 1,
        "title": tank["title"],
        "description": "",
        "current_pollution": pollution.current(tank, now, config),
        "tank_bg_id": tank["tank_bg_id"],
        "purchased_lighting": [],
        "slot": tank["slot"],
        "toxic_fish_count": 0,
        "toxic_fish_active": 0,
        "level_required": 1,
        "tank_items": tank_items(tank, now, config),
        "gravel_frame": 1,
        "gravel_id": tank["gravel_id"],
        "likes": 0,
        "player_rating": 0,
        "days_left": 0,
        "time_left": 0,
        "cleaner_days_left": 0,
        "cleaner_time_left": 0,
        "app_user_id": app_id,
        "is_neglected": 0,
        "lighting_id": tank["lighting_id"],
    }


def app_user(player, now, config):
    app_id = app_user_id(player["user_id"])
    return {
        "user_id": player["user_id"],
        "tpi": player["user_id"],
        "appUserId": app_id,
        "name": player["name"],
        "pictureUrl": "",
        "profileUrl": "",
        "app_friends": [],
        "coins": player["coins"],
        "actionPoints": player["pearls"],
        "xp": player["xp"],
        "userSnacks": 0,
        "userTanks": [user_tank(player, t, app_id, now, config) for t in player["tanks"]],
        "userFoods": [{"appUserId": app_id, "foodTypeId": int(k), "amount": v} for k, v in player["foods"].items()],
        "playingFriends": [],
        "isFan": 1,
        "HaveEmail": 0,
        "purchased_wallpapers": [],
        "orphan_popup": 0,
    }


@action("get_init_data", saves=False)
def get_init_data(ctx):
    now = int(time.time())
    user = app_user(ctx.player, now, ctx.config)
    return {
        "timestamp": now,
        "platform": catalog.PLATFORM,
        "phpVersion": "happyaquarium-server",
        "textVersion": 1,
        "swfVer": 1,
        "storeVersion": 1,
        "items": catalog.items(ctx.cdn),
        "parts": {},
        "tanks": catalog.tanks(ctx.cdn),
        "tankProgressions": [],
        "gravel": {str(k): v for k, v in catalog.GRAVEL.items()},
        "wallpaper": {str(k): v for k, v in catalog.WALLPAPERS.items()},
        "storeItems": catalog.store_items(),
        "storeFoods": {},
        "foodTypes": {str(k): v for k, v in catalog.FOOD_TYPES.items()},
        "food_items": catalog.food_items(),
        "generic_items": catalog.generic_items(),
        "owner": user,
        "player": user,
        "flashAppUserMetaData": ctx.player["meta"],
        "userCompositeItems": {},
        # 101XP's $2.99/month paywall shows when date_subscription - date_subscription_current <= 0
        "date_subscription": now + ctx.config["subscription_days"] * 86400,
        "date_subscription_current": now,
        "products": [],
        "appProducts": [],
        "subscriptionProducts": [],
        "giftsToBuy": [],
        "num_bad_loads": 0,
        "toolbar_compatible": 0,
        "can_do_hybrid_tutorial": 0,
        "user_gumball_bank_count": 0,
        "user_board_game_space": 0,
        "user_spin_collection": {},
        "collections": {},
        "collectionItems": {},
        "lighting_effects": {},
        "achievements": {},
        "maleNames": catalog.MALE_NAMES,
        "femaleNames": catalog.FEMALE_NAMES,
        "gameWinners": [],
        "midway_tickets": 0,
        "midway_game_purchases": 0,
        # The client throws on a wrong JSON type here (userAudience must be an array)
        "userAudience": [],
        "nextBigTanksCosts": -1,
        "currentBigTankProgression": -1,
        "maxBigTankProgression": -1,
    }
