from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.schemas import RecipeCartRequest, RecipeCartItem
from services import spoonacular, matcher

router = APIRouter()


@router.post("/recipes/to-cart", response_model=list[RecipeCartItem])
def recipe_to_cart(req: RecipeCartRequest, db: Session = Depends(get_db)):
    recipe = spoonacular.search_recipe(req.recipe_name)
    if not recipe:
        return []

    ingredients = spoonacular.get_recipe_ingredients(recipe["id"])
    results = []
    for ingredient in ingredients:
        matched = matcher.match_ingredient(ingredient, db)
        results.append(
            RecipeCartItem(
                ingredient=ingredient,
                matched_product=matched["name"] if matched else None,
                price=matched["price"] if matched else None,
                match_score=matched.get("match_score") if matched else None,
            )
        )
    return results
