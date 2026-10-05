OK = {"error": 0}
ERR_UNKNOWN_ITEM = 1
ERR_NOT_ENOUGH_MONEY = 2


def pay(player, coins, pearls):
    if player["coins"] < coins or player["pearls"] < pearls:
        return False
    player["coins"] -= coins
    player["pearls"] -= pearls
    return True


def find_tank(player, user_tank_id):
    for tank in player["tanks"]:
        if tank["user_tank_id"] == user_tank_id:
            return tank
    return player["tanks"][0]
