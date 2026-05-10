from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PricePoint(BaseModel):
    price: float
    observed_at: datetime


class ProductPrice(BaseModel):
    product_id: int
    name: str
    brand: Optional[str] = None
    store: str
    current_price: float
    unit: Optional[str] = None


class SaleItem(BaseModel):
    name: str
    store: str
    current_price: float
    avg_30d: float
    pct_drop: float


class CartItem(BaseModel):
    name: str
    price: float
    quantity: int


class CartRequest(BaseModel):
    items: list[str]
    budget: float = 50.0
    store: str = "kroger"


class CartResponse(BaseModel):
    total_cost: float
    savings: float
    items: list[CartItem]
    store_recommendation: str
    budget_remaining: float
    substitutions: list[dict] = []


class MealPlanRequest(BaseModel):
    budget: float = 50.0
    calories_per_day: int = 2000


class MealPlanResponse(BaseModel):
    meals: dict
    grocery_list: list[CartItem]
    total_cost: float


class RecipeCartRequest(BaseModel):
    recipe_name: str


class RecipeCartItem(BaseModel):
    ingredient: str
    matched_product: Optional[str]
    price: Optional[float]
    match_score: Optional[float]


class WatchlistAddRequest(BaseModel):
    user_email: str
    product_id: int
    target_price: Optional[float] = None
