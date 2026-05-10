import os
import asyncio
import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from db import Session
from routers import prices, optimize, recipes

connected_clients: list[WebSocket] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_price_broadcaster())
    yield
    task.cancel()


app = FastAPI(title="GroceryAI API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(prices.router)
app.include_router(optimize.router)
app.include_router(recipes.router)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.websocket("/ws/prices")
async def websocket_prices(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connected_clients.remove(ws)


async def _price_broadcaster():
    while True:
        await asyncio.sleep(60)
        if not connected_clients:
            continue
        try:
            with Session() as db:
                rows = db.execute(text("""
                    SELECT DISTINCT ON (p.id)
                        p.id, p.name, s.name, po.price
                    FROM products p
                    JOIN stores s ON p.store_id = s.id
                    JOIN price_observations po ON po.product_id = p.id
                    ORDER BY p.id, po.observed_at DESC
                    LIMIT 50
                """)).fetchall()
            payload = json.dumps([
                {"id": r[0], "name": r[1], "store": r[2], "price": float(r[3])}
                for r in rows
            ])
            dead = []
            for client in connected_clients:
                try:
                    await client.send_text(payload)
                except Exception:
                    dead.append(client)
            for d in dead:
                connected_clients.remove(d)
        except Exception:
            pass
