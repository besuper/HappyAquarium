import time

from . import catalog
from ..storage import app_user_id

TEN_YEARS = 10 * 365 * 86400


def user_tank(player, tank, app_id):
    """UserTank.parseFromJSON row."""
    return {
        "user_id": player["user_id"],
        "user_tank_id": tank["user_tank_id"],
        "tank_id": tank["tank_id"],
        "is_loaded": 1,
        "title": tank["title"],
        "description": "",
        "current_pollution": tank["pollution"],
        "tank_bg_id": tank["tank_bg_id"],
        "purchased_lighting": [],
        "slot": tank["slot"],
        "toxic_fish_count": 0,
        "toxic_fish_active": 0,
        "level_required": 1,
        "tank_items": tank["items"],
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


def app_user(player):
    """AppUser.parseFromJSON row; the same object is sent as owner and player."""
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
        "userTanks": [user_tank(player, t, app_id) for t in player["tanks"]],
        "playingFriends": [],
        "isFan": 1,
        "HaveEmail": 0,
        "purchased_wallpapers": [],
        "orphan_popup": 0,
    }


def build(player, cdn):
    now = int(time.time())
    user = app_user(player)
    return {
        "timestamp": now,
        "platform": catalog.PLATFORM,
        "phpVersion": "happyaquarium-server",
        "textVersion": 1,
        "swfVer": 1,
        "storeVersion": 1,
        "items": catalog.items(cdn),
        "parts": {},
        "tanks": catalog.tanks(cdn),
        "tankProgressions": [],
        "gravel": {str(k): v for k, v in catalog.GRAVEL.items()},
        "wallpaper": {str(k): v for k, v in catalog.WALLPAPERS.items()},
        "storeItems": catalog.store_items(),
        "storeFoods": {},
        "foodTypes": {},
        "food_items": {},
        "generic_items": {},
        "owner": user,
        "player": user,
        "flashAppUserMetaData": player["meta"],
        "userCompositeItems": {},
        # The client shows a paywall when date_subscription - date_subscription_current <= 0 and asking for a $2.99/month subscription (???)
        "date_subscription": now + TEN_YEARS,
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
        "maleNames": ["Bubbles", "Finn", "Gill"],
        "femaleNames": ["Coral", "Pearl", "Marina"],
        "gameWinners": [],
        "midway_tickets": 0,
        "midway_game_purchases": 0,
        "userAudience": [],
        "nextBigTanksCosts": -1,
        "currentBigTankProgression": -1,
        "maxBigTankProgression": -1,
    }
