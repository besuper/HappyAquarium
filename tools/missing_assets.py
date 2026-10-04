"""List the art files referenced by the original catalogue that are not in assets/.

Usage: python tools/missing_assets.py [--markdown]

Any file found (browser cache, backups...) can be dropped into assets/ at the printed
path: the server then sends the item to the client automatically.
"""
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from happyaquarium.game.catalog import ALL_ITEMS, art_path, has_art, _CATALOGUE  # noqa: E402

ITEM_TYPES = {1: "Fish", 2: "Props", 4: "Corals", 5: "Chests", 6: "Crawlers", 7: "Feeders", 8: "Cleaners", 9: "Friends"}


def main(markdown):
    missing = defaultdict(list)
    total = 0
    for raw in _CATALOGUE["items"].values():
        item = ALL_ITEMS[int(raw["itemId"])]
        for path in {art_path(raw["artUrl"]), art_path(raw.get("babyArtUrl"))} - {""}:
            total += 1
            if not has_art(path):
                missing[ITEM_TYPES.get(item["item_type"], "Other")].append((path, item["title"]))
    count = sum(len(v) for v in missing.values())
    print(f"{count} of {total} art files missing\n")
    for group in sorted(missing):
        print(f"## {group}\n" if markdown else f"[{group}]")
        for path, title in sorted(missing[group]):
            print(f"- `{path}` ({title})" if markdown else f"  {path}  ({title})")
        print()


if __name__ == "__main__":
    main("--markdown" in sys.argv)
