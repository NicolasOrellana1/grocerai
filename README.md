# GroceryAI

A full-stack grocery price intelligence platform that scrapes real-time prices from Kroger, Walmart, and Aldi, then uses linear programming and fuzzy matching to optimize your shopping cart, generate meal plans, and send price alerts.

## Features

- **Price Comparison** — Track and compare prices across Kroger, Walmart, and Aldi with 30-day history and sale detection
- **Smart Cart Optimization** — Budget-constrained cart optimization using linear programming, with multi-store routing and cheaper substitution suggestions
- **Meal Planner** — AI-generated 7-day meal plans via Spoonacular, with automatic grocery list deduplication and budget awareness
- **Recipe to Cart** — Search any recipe and convert its ingredients to a priced shopping list
- **Real-time Price Alerts** — WebSocket price feed and email alerts (SendGrid) when watchlist items hit target prices
- **Pipeline Monitor** — Live dashboard for scraper task health and WebSocket connection status

## Architecture

```
groceryai/
├── backend/        # FastAPI REST API + WebSocket server
├── frontend/       # React + Vite SPA
├── scraper/        # Celery workers (Playwright + Kroger OAuth)
├── db/             # PostgreSQL + TimescaleDB schema
└── docker-compose.yml
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, Vite, Tailwind CSS, Zustand, Recharts |
| Backend | FastAPI, SQLAlchemy 2, PuLP, RapidFuzz, WebSockets |
| Scraping | Celery, Playwright, Celery Beat, Flower |
| Database | PostgreSQL 16 + TimescaleDB (hypertable for price time-series) |
| Infra | Docker Compose, Redis |

## Quick Start

### Prerequisites

- Docker & Docker Compose
- API keys: [Spoonacular](https://spoonacular.com/food-api), [Kroger Developer](https://developer.kroger.com/), [SendGrid](https://sendgrid.com/) (optional)

### 1. Configure environment

Copy `.env` and fill in your credentials:

```env
DB_PASSWORD=yourpassword
KROGER_CLIENT_ID=your_kroger_client_id
KROGER_CLIENT_SECRET=your_kroger_client_secret
KROGER_ZIP_CODE=10001
SPOONACULAR_API_KEY=your_spoonacular_key
SENDGRID_API_KEY=your_sendgrid_key        # optional, for email alerts
DATABASE_URL=postgresql://postgres:yourpassword@db:5432/groceryai
REDIS_URL=redis://redis:6379/0
VITE_API_URL=http://localhost:8000
APP_URL=http://localhost:3000
```

### 2. Start all services

```bash
docker-compose up -d
```

### 3. Access the app

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API + Swagger | http://localhost:8000/docs |
| Celery Flower | http://localhost:5555 |

The database is initialized automatically from `db/init.sql` on first run.

## Local Development (without Docker)

**Backend**
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev   # http://localhost:5173
```

**Scraper workers** (requires Redis + Postgres running)
```bash
cd scraper
pip install -r requirements.txt

# Terminal 1 — worker
celery -A tasks worker --loglevel=info

# Terminal 2 — Beat scheduler (runs scrapers every 15 min)
celery -A tasks beat --loglevel=info

# Terminal 3 — Flower UI (optional)
celery -A tasks flower --port=5555
```

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| GET | `/prices` | Latest prices for all products |
| GET | `/prices/sales` | Items with 10%+ discount vs 30-day avg |
| GET | `/prices/{id}/history` | 30-day price history for a product |
| POST | `/watchlist/add` | Add product to price watchlist |
| POST | `/optimize/cart` | Optimize cart within budget |
| POST | `/optimize/meal-plan` | Generate 7-day meal plan |
| POST | `/recipes/to-cart` | Convert recipe to priced ingredient list |
| WS | `/ws/prices` | Real-time price push notifications |

## How It Works

**Scraping** — Celery Beat triggers store scrapers every 15 minutes. Kroger uses OAuth client credentials; Walmart and Aldi use Playwright headless browsing. All price observations land in a TimescaleDB hypertable for efficient time-series queries.

**Cart Optimization** — `POST /optimize/cart` feeds item prices into a PuLP linear program that minimizes total cost under a budget constraint. If splitting across two stores saves more than the $3 estimated trip overhead, it recommends multi-store routing.

**Ingredient Matching** — RapidFuzz matches recipe ingredient strings to product names with an 80% similarity threshold, normalizing away qualifiers like "fresh", "chopped", or "sliced".

**Real-time Updates** — A background task broadcasts price changes over WebSocket every 60 seconds; the frontend reconnects automatically on disconnect.

## Project Status

Weeks 1–4 complete:
- [x] Database schema + TimescaleDB hypertable
- [x] Kroger, Walmart, Aldi scrapers
- [x] Price comparison + watchlist API
- [x] Cart optimizer (linear programming)
- [x] Meal planner + recipe-to-cart (Spoonacular)
- [x] Email alerts (SendGrid)
- [x] React frontend with all feature pages
- [x] Docker Compose orchestration
