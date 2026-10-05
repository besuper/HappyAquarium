from . import action
from ._common import OK


@action("populate_alerts", saves=False)
def populate_alerts(ctx):
    return {**OK, "popupItems": {}, "actionItems": {}, "app_request_data": [], "request_map": {}}


@action("get_expeditions", saves=False)
def get_expeditions(ctx):
    return {**OK, "expeditionItems": [], "userExpeditions": [], "reward_data": {}}


@action("get_constructs", saves=False)
def get_constructs(ctx):
    return {**OK, "constructItems": {}, "userConstructs": {}}


@action("prune_user", saves=False)
def prune_user(ctx):
    return OK
