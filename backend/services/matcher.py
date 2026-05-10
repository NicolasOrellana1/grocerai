from rapidfuzz import fuzz
from sqlalchemy.orm import Session
from sqlalchemy import text


def match_ingredient(ingredient: str, db: Session, threshold: int = 60) -> dict | None:
    rows = db.execute(
        text("""
            SELECT p.id, p.name, p.brand, s.name AS store, po.price
            FROM products p
            JOIN stores s ON p.store_id = s.id
            JOIN LATERAL (
                SELECT price FROM price_observations
                WHERE product_id = p.id
                ORDER BY observed_at DESC
                LIMIT 1
            ) po ON TRUE
        """)
    ).fetchall()

    best, best_score = None, 0
    for row in rows:
        product_name = f"{row[2] or ''} {row[1]}".strip()
        score = fuzz.token_sort_ratio(ingredient.lower(), product_name.lower())
        if score > best_score:
            best_score = score
            best = {"id": row[0], "name": row[1], "brand": row[2], "store": row[3], "price": float(row[4])}

    if best and best_score >= threshold:
        best["match_score"] = best_score
        return best
    return None


def deduplicate_ingredients(ingredient_lists: list[list[str]]) -> list[str]:
    seen: dict[str, str] = {}
    for ingredients in ingredient_lists:
        for ing in ingredients:
            key = ing.lower().strip()
            normalized = _normalize(key)
            if normalized not in seen:
                seen[normalized] = ing
    return list(seen.values())


def _normalize(name: str) -> str:
    stop_words = {"fresh", "dried", "chopped", "sliced", "diced", "large", "small", "medium", "whole"}
    tokens = [t for t in name.split() if t not in stop_words]
    return " ".join(sorted(tokens))
