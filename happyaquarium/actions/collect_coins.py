import time

from . import action
from ._common import ERR_UNKNOWN_ITEM
from ..game import treasure


@action("collect_coins")
def collect_coins(ctx):
    player = ctx.player
    now = int(time.time())
    tank_item_id = int(ctx.params.get("tank_item_id", -1))
    for tank in player["tanks"]:
        for row in tank["items"]:
            if row["tankItemId"] == tank_item_id and treasure.is_chest(row) and treasure.has_coins(row, now, ctx.config):
                coins = treasure.payout(tank, now, ctx.config)
                row["last_coin_collect"] = now
                player["coins"] += coins
                # The client adds coin_payout to its own total and ignores "coins" in this reply
                return {"error": 0, "coin_payout": coins, "coins": player["coins"]}
    return {"error": ERR_UNKNOWN_ITEM, "coin_payout": 0}
