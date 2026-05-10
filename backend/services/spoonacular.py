import os
import requests

API_KEY = os.getenv("SPOONACULAR_API_KEY", "")
BASE_URL = "https://api.spoonacular.com"


def search_recipe(name: str) -> dict | None:
    resp = requests.get(
        f"{BASE_URL}/recipes/complexSearch",
        params={"query": name, "apiKey": API_KEY, "number": 1},
        timeout=10,
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


def get_recipe_ingredients(recipe_id: int) -> list[str]:
    resp = requests.get(
        f"{BASE_URL}/recipes/{recipe_id}/ingredientWidget.json",
        params={"apiKey": API_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    ingredients = []
    for item in data.get("ingredients", []):
        name = item.get("name", "")
        if name:
            ingredients.append(name)
    return ingredients


def generate_meal_plan(calories: int = 2000) -> dict:
    resp = requests.get(
        f"{BASE_URL}/mealplanner/generate",
        params={"timeFrame": "week", "targetCalories": calories, "apiKey": API_KEY},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def extract_all_ingredients(meal_plan: dict) -> list[list[str]]:
    all_ingredient_lists = []
    week = meal_plan.get("week", {})
    for day_data in week.values():
        meals = day_data.get("meals", [])
        for meal in meals:
            recipe_id = meal.get("id")
            if recipe_id:
                try:
                    ingredients = get_recipe_ingredients(recipe_id)
                    all_ingredient_lists.append(ingredients)
                except Exception:
                    pass
    return all_ingredient_lists


def format_meal_plan_grid(meal_plan: dict) -> dict:
    days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    grid = {}
    week = meal_plan.get("week", {})
    for day in days:
        day_data = week.get(day, {})
        meals = day_data.get("meals", [])
        grid[day] = {
            "breakfast": meals[0].get("title") if len(meals) > 0 else None,
            "lunch": meals[1].get("title") if len(meals) > 1 else None,
            "dinner": meals[2].get("title") if len(meals) > 2 else None,
        }
    return grid
