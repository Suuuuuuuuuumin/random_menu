import json
from pathlib import Path

RECOMMENDED_RATIOS = {
    "protein": 0.25,
    "carbs": 0.5,
    "fat": 0.25,
}


def load_json(path):
    with open(path) as f:
        return json.load(f)


def total_macros(meals):
    totals = {"protein": 0, "carbs": 0, "fat": 0}
    for meal in meals:
        for k in totals:
            totals[k] += meal.get(k, 0)
    return totals


def macro_ratio(macros):
    total = sum(macros.values())
    if total == 0:
        return {k: 0 for k in macros}
    return {k: macros[k] / total for k in macros}


def score(macros):
    ratios = macro_ratio(macros)
    return sum((ratios[k] - RECOMMENDED_RATIOS[k]) ** 2 for k in ratios)


def recommend(meal_history_path: str, menus_path: str):
    meals = load_json(meal_history_path)
    menus = load_json(menus_path)

    consumed = total_macros(meals)

    best_menu = None
    best_score = float("inf")

    for menu in menus:
        combined = {
            k: consumed[k] + menu.get(k, 0) for k in consumed
        }
        s = score(combined)
        if s < best_score:
            best_score = s
            best_menu = menu

    return best_menu


def main():
    history_path = Path("meal_history.json")
    menus_path = Path("menus.json")

    best = recommend(history_path, menus_path)
    if best:
        print("Recommended menu:", best["name"])
    else:
        print("No recommendation found")


if __name__ == "__main__":
    main()
