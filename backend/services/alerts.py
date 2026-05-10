import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from sqlalchemy.orm import Session
from sqlalchemy import text

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "")
FROM_EMAIL = os.getenv("ALERT_FROM_EMAIL", "alerts@groceryai.app")
APP_URL = os.getenv("APP_URL", "http://localhost:3000")


def _get_sales(db: Session) -> list[dict]:
    rows = db.execute(text("""
        SELECT p.id, p.name, po_latest.price AS current_price,
               AVG(po_hist.price) AS avg_30d,
               ROUND((1 - po_latest.price / AVG(po_hist.price)) * 100, 1) AS pct_drop
        FROM products p
        JOIN price_observations po_hist ON po_hist.product_id = p.id
        JOIN LATERAL (
            SELECT price FROM price_observations
            WHERE product_id = p.id
            ORDER BY observed_at DESC
            LIMIT 1
        ) po_latest ON TRUE
        WHERE po_hist.observed_at >= NOW() - INTERVAL '30 days'
        GROUP BY p.id, p.name, po_latest.price
        HAVING po_latest.price < AVG(po_hist.price) * 0.90
    """)).fetchall()
    return [
        {"product_id": r[0], "name": r[1], "current_price": float(r[2]),
         "avg_30d": float(r[3]), "pct_drop": float(r[4])}
        for r in rows
    ]


def _get_matching_watchlist(sale_product_ids: list[int], db: Session) -> list[dict]:
    if not sale_product_ids:
        return []
    rows = db.execute(
        text("""
            SELECT w.user_email, w.product_id, w.target_price
            FROM watchlist w
            WHERE w.product_id = ANY(:ids)
        """),
        {"ids": sale_product_ids},
    ).fetchall()
    return [{"user_email": r[0], "product_id": r[1], "target_price": r[2]} for r in rows]


def _send_alert(email: str, item: dict) -> None:
    if not SENDGRID_API_KEY:
        print(f"[alerts] SENDGRID_API_KEY not set — skipping email to {email}")
        return

    body = f"""
<h2>Price Drop Alert: {item['name']}</h2>
<p>Current price: <strong>${item['current_price']:.2f}</strong></p>
<p>30-day average: ${item['avg_30d']:.2f}</p>
<p>Discount: <strong>{item['pct_drop']}% off</strong></p>
<p><a href="{APP_URL}/prices">View in GroceryAI</a></p>
"""
    message = Mail(
        from_email=FROM_EMAIL,
        to_emails=email,
        subject=f"GroceryAI: {item['name']} is {item['pct_drop']}% off!",
        html_content=body,
    )
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        sg.send(message)
        print(f"[alerts] Sent alert to {email} for {item['name']}")
    except Exception as e:
        print(f"[alerts] Failed to send to {email}: {e}")


def run_sale_alerts(db: Session) -> int:
    sales = _get_sales(db)
    if not sales:
        return 0

    sale_map = {s["product_id"]: s for s in sales}
    watchlist = _get_matching_watchlist(list(sale_map.keys()), db)

    sent = 0
    for entry in watchlist:
        sale = sale_map.get(entry["product_id"])
        if not sale:
            continue
        if entry["target_price"] is not None and sale["current_price"] > float(entry["target_price"]):
            continue
        _send_alert(entry["user_email"], sale)
        sent += 1

    return sent
