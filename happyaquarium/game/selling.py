import math

from . import growth, levels

# Same values as TankItem.getSellAmount / getXpSellAmount in the client
AGE_MULTIPLIERS = {growth.EGG: 0, 0: 0.3, 1: 0.5, 2: 0.9, 3: 0.9, growth.ADULT: 1.1}
NON_FISH_MULTIPLIER = 0.8
EGG_PRICE = 3
TRAINING_BONUS = [0, 0.01, 0.02, 0.04, 0.07, 0.1, 0.14, 0.2]
MAX_TRAINING_BONUS = 400
LEVEL_TO_GET_XP = 15
PREMIUM_FISH_LEVEL = 110


def price(row, item, now):
    age_level = growth.level(row, now)

    if age_level == growth.NONE:
        return math.floor(item["coin_cost"] * NON_FISH_MULTIPLIER)

    if age_level == growth.EGG:
        return EGG_PRICE

    coins = math.floor(item["coin_cost"] * AGE_MULTIPLIERS[age_level])
    trick = row.get("trickLevel", 0)
    bonus = TRAINING_BONUS[trick] if trick < len(TRAINING_BONUS) else 0

    return coins + min(math.floor(coins * bonus), MAX_TRAINING_BONUS)


def xp(row, item, player_xp, now):
    player_level = levels.level_for_xp(player_xp)

    if growth.level(row, now) != growth.ADULT or player_level < LEVEL_TO_GET_XP:
        return 0

    fish_level = PREMIUM_FISH_LEVEL if item["action_point_cost"] > 0 else item["level_required"]
    days_to_mature = item["growth_rate"] * growth.ADULT / 3600 / 24
    
    return math.floor(days_to_mature * fish_level * player_level / 30) + 1
