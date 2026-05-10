from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db import get_db
from models.schemas import CartRequest, CartResponse, MealPlanRequest, MealPlanResponse
from services import optimizer as opt_service
from services import spoonacular, matcher

router = APIRouter()


@router.post("/optimize/cart", response_model=CartResponse)
def optimize_cart(req: CartRequest, db: Session = Depends(get_db)):
    result = opt_service.optimize_cart(req.items, req.budget, req.store, db)
    return CartResponse(**result)


@router.post("/optimize/meal-plan", response_model=MealPlanResponse)
def optimize_meal_plan(req: MealPlanRequest, db: Session = Depends(get_db)):
    plan = spoonacular.generate_meal_plan(req.calories_per_day)
    ingredient_lists = spoonacular.extract_all_ingredients(plan)
    deduped = matcher.deduplicate_ingredients(ingredient_lists)

    grocery_items = []
    total = 0.0
    for ingredient in deduped:
        matched = matcher.match_ingredient(ingredient, db)
        if matched:
            grocery_items.append({
                "name": matched["name"],
                "price": matched["price"],
                "quantity": 1,
            })
            total += matched["price"]
            if total >= req.budget:
                break

    return MealPlanResponse(
        meals=spoonacular.format_meal_plan_grid(plan),
        grocery_list=grocery_items,
        total_cost=round(total, 2),
    )
