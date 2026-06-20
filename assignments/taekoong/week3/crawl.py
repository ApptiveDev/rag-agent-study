import requests
from pathlib import Path

MOBS = [
    "Creeper",
    "Zombie",
    "Skeleton",
    "Spider",
    "Enderman",
    "Witch",
    "Blaze",
    "Ghast",
    "Slime",
    "Wither"
]

ITEMS = [
    "Diamond",
    "Iron Ingot",
    "Gold Ingot",
    "Emerald",
    "Coal",
    "Obsidian",
    "Ender Pearl",
    "Blaze Rod",
    "Bow",
    "Shield",
    "Torch",
    "Crafting Table",
    "Furnace",
    "Chest",
    "Bed",
    "Diamond Sword",
    "Diamond Pickaxe",
    "Golden Apple",
    "Enchanting Table",
    "Anvil"
]

RECIPES = [
    "Torch",
    "Crafting Table",
    "Furnace",
    "Chest",
    "Bed",
    "Diamond Sword",
    "Diamond Pickaxe",
    "Golden Apple",
    "Enchanting Table",
    "Anvil"
]

API_URL = "https://minecraft.wiki/api.php"


def get_page_text(title: str):
    params = {
        "action": "query",
        "prop": "extracts",
        "titles": title,
        "format": "json",
        "explaintext": True,
        "redirects": 1,
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    pages = response.json()["query"]["pages"]

    for page in pages.values():
        return page.get("extract", "")

    return ""


def save_doc(category: str, title: str, text: str):
    folder = Path("data") / category
    folder.mkdir(parents=True, exist_ok=True)

    filename = title.lower().replace(" ", "_") + ".txt"

    with open(folder / filename, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    for mob in MOBS:
        print(f"[MOB] {mob}")
        text = get_page_text(mob)
        save_doc("mobs", mob, text)

    for item in ITEMS:
        print(f"[ITEM] {item}")
        text = get_page_text(item)
        save_doc("items", item, text)

    for recipe in RECIPES:
        print(f"[RECIPTE] {recipe}")
        text = get_page_text(recipe)
        save_doc("recipes", recipe, text)

if __name__ == "__main__":
    main()