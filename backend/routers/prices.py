from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from db import get_db
from models.schemas import ProductPrice, SaleItem, PricePoint, WatchlistAddRequest

router = APIRouter()


@router.get("/prices", response_model=list[ProductPrice])
def get_latest_prices(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT DISTINCT ON (p.id)
            p.id, p.name, p.brand, s.name AS store, po.price, p.unit
        FROM products p
        JOIN stores s ON p.store_id = s.id
        JOIN price_observations po ON po.product_id = p.id
        ORDER BY p.id, po.observed_at DESC
    """)).fetchall()
    return [
        ProductPrice(
            product_id=r[0], name=r[1], brand=r[2],
            store=r[3], current_price=float(r[4]), unit=r[5]
        )
        for r in rows
    ]


@router.get("/prices/sales", response_model=list[SaleItem])
def get_sales(db: Session = Depends(get_db)):
    rows = db.execute(text("""
        SELECT p.name, s.name AS store, po_latest.price AS current_price,
               AVG(po_hist.price) AS avg_30d,
               ROUND((1 - po_latest.price / AVG(po_hist.price)) * 100, 1) AS pct_drop
        FROM products p
        JOIN stores s ON p.store_id = s.id
        JOIN price_observations po_hist ON po_hist.product_id = p.id
        JOIN LATERAL (
            SELECT price FROM price_observations
            WHERE product_id = p.id
            ORDER BY observed_at DESC
            LIMIT 1
        ) po_latest ON TRUE
        WHERE po_hist.observed_at >= NOW() - INTERVAL '30 days'
        GROUP BY p.name, s.name, po_latest.price
        HAVING po_latest.price < AVG(po_hist.price) * 0.90
        ORDER BY pct_drop DESC
    """)).fetchall()
    return [
        SaleItem(
            name=r[0], store=r[1], current_price=float(r[2]),
            avg_30d=float(r[3]), pct_drop=float(r[4])
        )
        for r in rows
    ]


@router.get("/prices/{product_id}/history", response_model=list[PricePoint])
def get_price_history(product_id: int, db: Session = Depends(get_db)):
    rows = db.execute(
        text("""
            SELECT price, observed_at
            FROM price_observations
            WHERE product_id = :pid
              AND observed_at >= NOW() - INTERVAL '30 days'
            ORDER BY observed_at ASC
        """),
        {"pid": product_id},
    ).fetchall()
    return [PricePoint(price=float(r[0]), observed_at=r[1]) for r in rows]


@router.post("/watchlist/add")
def add_to_watchlist(req: WatchlistAddRequest, db: Session = Depends(get_db)):
    db.execute(
        text("""
            INSERT INTO watchlist (user_email, product_id, target_price)
            VALUES (:email, :pid, :target)
        """),
        {"email": req.user_email, "pid": req.product_id, "target": req.target_price},
    )
    db.commit()
    return {"status": "added"}
