from pulp import LpProblem, LpVariable, LpMinimize, lpSum, LpStatus, value
from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from sqlalchemy import text

TRIP_COST = 3.00


def _fetch_products(db: Session, store: str) -> list[dict]:
    rows = db.execute(
        text("""
            SELECT p.id, p.name, p.brand, po.price
            FROM products p
            JOIN stores s ON p.store_id = s.id
            JOIN LATERAL (
                SELECT price FROM price_observations
                WHERE product_id = p.id
                ORDER BY observed_at DESC
                LIMIT 1
            ) po ON TRUE
            WHERE s.name = :store
        """),
        {"store": store},
    ).fetchall()
    return [{"id": r[0], "name": r[1], "brand": r[2], "price": float(r[3])} for r in rows]


def _match_item(query: str, products: list[dict], threshold: int = 60) -> dict | None:
    best, best_score = None, 0
    for p in products:
        score = fuzz.token_sort_ratio(query.lower(), p["name"].lower())
        if score > best_score:
            best_score, best = score, p
    return best if best_score >= threshold else None


def optimize_cart(items: list[str], budget: float, store: str, db: Session) -> dict:
    products = _fetch_products(db, store)
    matched = []
    for item in items:
        product = _match_item(item, products)
        if product:
            matched.append(product)

    if not matched:
        return {
            "total_cost": 0.0,
            "savings": budget,
            "items": [],
            "store_recommendation": store,
            "budget_remaining": budget,
            "substitutions": [],
        }

    prob = LpProblem("cart_optimizer", LpMinimize)
    qty = {p["id"]: LpVariable(f"qty_{p['id']}", lowBound=1, cat="Integer") for p in matched}

    prob += lpSum(p["price"] * qty[p["id"]] for p in matched)
    prob += lpSum(p["price"] * qty[p["id"]] for p in matched) <= budget

    prob.solve()

    if LpStatus[prob.status] != "Optimal":
        total = sum(p["price"] for p in matched)
        cart_items = [{"name": p["name"], "price": p["price"], "quantity": 1} for p in matched]
        return {
            "total_cost": round(total, 2),
            "savings": round(budget - total, 2),
            "items": cart_items,
            "store_recommendation": store,
            "budget_remaining": round(budget - total, 2),
            "substitutions": _find_substitutions(matched, products),
        }

    cart_items = []
    total = 0.0
    for p in matched:
        q = int(value(qty[p["id"]]) or 1)
        cost = p["price"] * q
        total += cost
        cart_items.append({"name": p["name"], "price": p["price"], "quantity": q})

    return {
        "total_cost": round(total, 2),
        "savings": round(budget - total, 2),
        "items": cart_items,
        "store_recommendation": store,
        "budget_remaining": round(budget - total, 2),
        "substitutions": _find_substitutions(matched, products),
    }


def _find_substitutions(matched: list[dict], all_products: list[dict]) -> list[dict]:
    substitutions = []
    for item in matched:
        for candidate in all_products:
            if candidate["id"] == item["id"]:
                continue
            score = fuzz.token_sort_ratio(item["name"].lower(), candidate["name"].lower())
            if score >= 80 and candidate["price"] < item["price"]:
                substitutions.append({
                    "original": item["name"],
                    "original_price": item["price"],
                    "substitute": candidate["name"],
                    "substitute_price": candidate["price"],
                    "savings": round(item["price"] - candidate["price"], 2),
                })
                break
    return substitutions


def check_multistore_routing(items: list[str], budget: float, stores: list[str], db: Session) -> dict:
    store_results = {}
    for store in stores:
        try:
            result = optimize_cart(items, budget, store, db)
            store_results[store] = result["total_cost"]
        except Exception:
            store_results[store] = float("inf")

    if len(store_results) < 2:
        best_store = min(store_results, key=store_results.get)
        return {"recommended_store": best_store, "split_shopping": False, "reason": "Only one store available"}

    sorted_stores = sorted(store_results.items(), key=lambda x: x[1])
    cheapest = sorted_stores[0]
    second = sorted_stores[1]

    savings = second[1] - cheapest[1]
    split_worthwhile = savings > TRIP_COST

    return {
        "recommended_store": cheapest[0],
        "cheapest_total": round(cheapest[1], 2),
        "second_store": second[0],
        "second_total": round(second[1], 2),
        "potential_savings": round(savings, 2),
        "split_shopping": split_worthwhile,
        "trip_cost": TRIP_COST,
        "reason": f"Splitting saves ${savings:.2f} which {'exceeds' if split_worthwhile else 'does not exceed'} the ${TRIP_COST} trip cost",
    }
