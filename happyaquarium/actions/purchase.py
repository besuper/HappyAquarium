from . import action
from ._common import ERR_NOT_ENOUGH_MONEY, ERR_UNKNOWN_ITEM, find_tank, pay
from ..game import catalog
from ..storage import new_tank_item


def buy_item(ctx, item_id, quantity):
    item = catalog.ITEMS[item_id]
    if not pay(ctx.player, item["coin_cost"] * quantity, item["action_point_cost"] * quantity):
        return {"error": ERR_NOT_ENOUGH_MONEY}

    player = ctx.player
    tank = find_tank(player, int(ctx.params.get("user_tank_id", 1)))
    bought = []
    for _ in range(quantity):
        row = new_tank_item(player["next_tank_item_id"], item_id, ctx.params.get("item_name") or item["title"],
                            user_tank_id=tank["user_tank_id"], sex=int(ctx.params.get("sex", 1)), age=0)
        player["next_tank_item_id"] += 1
        tank["items"].append(row)
        bought.append(row)
    return {"error": 0, "items": bought, "coins": player["coins"], "pearls": player["pearls"]}


def buy_food(ctx, food, quantity):
    player = ctx.player
    if not pay(player, food["coin_cost"] * quantity, food["action_point_cost"] * quantity):
        return {"error": ERR_NOT_ENOUGH_MONEY}
    food_type = str(catalog.FOOD_ITEM_TYPES[food["item_type"]])
    player["foods"][food_type] = player["foods"].get(food_type, 0) + food["food_amount"] * quantity

    return {"error": 0, "foods": [{"food_type_id": int(food_type), "amount": player["foods"][food_type]}],
            "coins": player["coins"], "pearls": player["pearls"]}


@action("purchase")
def purchase(ctx):
    store_id = int(ctx.params.get("store_item_id", -1))
    quantity = max(1, int(ctx.params.get("quantity", 1)))
    if store_id in catalog.FOOD_STORE:
        reply = buy_food(ctx, catalog.FOOD_ITEMS[catalog.FOOD_STORE[store_id]], quantity)
    elif store_id in catalog.STORE:
        reply = buy_item(ctx, catalog.STORE[store_id], quantity)
    else:
        reply = {"error": ERR_UNKNOWN_ITEM}
    return {"purchase_id": int(ctx.params.get("purchase_id", 0)), **reply}
