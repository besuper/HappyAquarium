import json
import time

from . import catalog
from ..storage import new_tank_item

OK = {"error": 0}
ERR_UNKNOWN_ITEM = 1
ERR_NOT_ENOUGH_MONEY = 2
MAX_XP_PER_FEEDING = 500

# Calls fired after boot whose answer only needs the right shape
# (DataManager.successAlert / successExpeditions / successConstruct).
STATIC_REPLIES = {
    "populate_alerts": {"error": 0, "popupItems": {}, "actionItems": {}, "app_request_data": [], "request_map": {}},
    "get_expeditions": {"error": 0, "expeditionItems": [], "userExpeditions": [], "reward_data": {}},
    "get_constructs": {"error": 0, "constructItems": {}, "userConstructs": {}},
    "prune_user": OK,
}


def find_tank(player, user_tank_id):
    for tank in player["tanks"]:
        if tank["user_tank_id"] == user_tank_id:
            return tank
    return player["tanks"][0]


def purchase(player, params):
    """comm/purchase.php -> Purchase.purchaseComplete -> DataManager.handleStandardResult."""
    reply = {"error": 0, "purchase_id": int(params.get("purchase_id", 0))}
    item_id = catalog.STORE.get(int(params.get("store_item_id", -1)))
    if item_id is None:
        return {**reply, "error": ERR_UNKNOWN_ITEM}
    item = catalog.ITEMS[item_id]
    quantity = max(1, int(params.get("quantity", 1)))
    coins = item["coin_cost"] * quantity
    pearls = item["action_point_cost"] * quantity
    if player["coins"] < coins or player["pearls"] < pearls:
        return {**reply, "error": ERR_NOT_ENOUGH_MONEY}

    player["coins"] -= coins
    player["pearls"] -= pearls
    tank = find_tank(player, int(params.get("user_tank_id", 1)))
    bought = []
    for _ in range(quantity):
        row = new_tank_item(player["next_tank_item_id"], item_id, params.get("item_name") or item["title"],
                            user_tank_id=tank["user_tank_id"], sex=int(params.get("sex", 1)), age=0)
        player["next_tank_item_id"] += 1
        tank["items"].append(row)
        bought.append(row)
    return {**reply, "items": bought, "coins": player["coins"], "pearls": player["pearls"]}


def feed_fish(player, params):
    """comm/feed_fish.php, sent by FishTank.updateFeedingData after a feeding session.

    Eating happens client-side; the client then reports the fish it fed (fish_json),
    its remaining food (user_foods_json) and its xp/coins (player_json).
    """
    now = int(time.time())
    items = {row["tankItemId"]: row for tank in player["tanks"] for row in tank["items"]}
    for fed in json.loads(params.get("fish_json") or "[]"):
        row = items.get(fed.get("tankItemId"))
        if row is None:
            continue
        row["hunger"] = max(0, min(100, int(fed.get("hunger", row["hunger"]))))
        row["last_hunger_update"] = now
        for key in ("xLocation", "yLocation", "zLocation"):
            if key in fed:
                row[key] = fed[key]
        row["flipped"] = 1 if fed.get("flipped") else 0

    for food in json.loads(params.get("user_foods_json") or "[]"):
        key = str(food.get("foodTypeId"))
        if key in player["foods"]:
            player["foods"][key] = max(0, min(player["foods"][key], int(food.get("amount", 0))))

    client_xp = int(json.loads(params.get("player_json") or "{}").get("xp") or 0)
    if player["xp"] < client_xp <= player["xp"] + MAX_XP_PER_FEEDING:
        player["xp"] = client_xp
    return OK


def set_key(player, params):
    """comm/set_key.php: client-side key/value metadata (tutorial step, settings...)."""
    data = json.loads(params.get("actiondata") or "{}")
    if "key" in data:
        player["meta"][str(data["key"])] = data.get("value")
    return OK


HANDLERS = {
    "purchase": purchase,
    "set_key": set_key,
    "feed_fish": feed_fish,
}
