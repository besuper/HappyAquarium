import time

from . import action
from ._common import ERR_UNKNOWN_ITEM
from ..game import catalog, selling, treasure


@action("sell_item")
def sell_item(ctx):
    player = ctx.player
    now = int(time.time())
    tank_item_id = int(ctx.params.get("tank_item_id", -1))

    for tank in player["tanks"]:
        for row in tank["items"]:
            if row["tankItemId"] != tank_item_id:
                continue

            item = catalog.ITEMS.get(row["itemId"])

            if item is None or treasure.is_chest(row):
                return {"error": ERR_UNKNOWN_ITEM}

            player["coins"] += selling.price(row, item, now)
            player["xp"] += selling.xp(row, item, player["xp"], now)
            tank["items"].remove(row)

            return {"error": 0, "coins": player["coins"], "xp": player["xp"]}
            
    return {"error": ERR_UNKNOWN_ITEM}
