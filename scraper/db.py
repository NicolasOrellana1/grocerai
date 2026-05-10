import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
Session = sessionmaker(bind=engine)

def save_price_observations(records: list[dict]):
    """
    Upserts products and inserts new price_observations.
    Each call from the scraper lands here.
    """
    with Session() as session:
        for record in records:
            # Find or create the product
            result = session.execute(
                text("""
                    INSERT INTO products (name, store_id)
                    SELECT :name, s.id FROM stores s WHERE s.name = :store
                    ON CONFLICT DO NOTHING
                    RETURNING id
                """),
                {"name": record["name"], "store": record["store"]}
            ).fetchone()

            if not result:
                result = session.execute(
                    text("SELECT p.id FROM products p JOIN stores s ON p.store_id = s.id WHERE p.name = :name AND s.name = :store"),
                    {"name": record["name"], "store": record["store"]}
                ).fetchone()

            if result:
                session.execute(
                    text("INSERT INTO price_observations (product_id, price) VALUES (:pid, :price)"),
                    {"pid": result[0], "price": record["price"]}
                )

        session.commit()