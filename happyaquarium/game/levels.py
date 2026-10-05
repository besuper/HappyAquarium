import math

MAX_LEVEL = 150
XP_FOR_SCRUB = 10


def _build_chart():
    chart = [0.0] * (MAX_LEVEL + 1)
    for level in range(2, MAX_LEVEL + 1):
        chart[level] = chart[level - 1] + 3 * math.pow(30, 1 + (level - 1) / 24)
    return [round(xp) for xp in chart]


XP_CHART = _build_chart()


def level_for_xp(xp):
    for level in range(1, MAX_LEVEL + 1):
        if xp < XP_CHART[level]:
            return level - 1
    return MAX_LEVEL


def level_up_pearls(old_level, new_level):
    return sum(level // 10 + 1 for level in range(max(1, old_level), new_level))


def gain_xp(player, new_xp):
    if new_xp <= player["xp"]:
        return
    old_level = level_for_xp(player["xp"])
    player["xp"] = new_xp
    player["pearls"] += level_up_pearls(old_level, level_for_xp(new_xp))


def xp_for_scrub(xp):
    level = level_for_xp(xp)
    return math.floor(XP_FOR_SCRUB * level ** 0.2) if level >= 15 else XP_FOR_SCRUB
