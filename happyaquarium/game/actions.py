import json

from . import catalog
from ..storage import new_tank_item

OK = {"error": 0}
ERR_UNKNOWN_ITEM = 1
ERR_NOT_ENOUGH_MONEY = 2

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


def set_key(player, params):
    """comm/set_key.php: client-side key/value metadata (tutorial step, settings...)."""
    data = json.loads(params.get("actiondata") or "{}")
    if "key" in data:
        player["meta"][str(data["key"])] = data.get("value")
    return OK


HANDLERS = {
    "purchase": purchase,
    "set_key": set_key,
}
