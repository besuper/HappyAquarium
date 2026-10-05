import json

from . import action
from ._common import OK


@action("set_key")
def set_key(ctx):
    data = json.loads(ctx.params.get("actiondata") or "{}")
    if "key" in data:
        ctx.player["meta"][str(data["key"])] = data.get("value")
    return OK
