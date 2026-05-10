import os
import asyncio
from celery import Celery
from db import save_price_observations
from stores.kroger import scrape_kroger
from stores.aldi import scrape_aldi

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

app = Celery("groceryai", broker=REDIS_URL, backend=REDIS_URL)

app.conf.task_acks_late = True
app.conf.task_reject_on_worker_lost = True

app.conf.beat_schedule = {
    "scrape-kroger-every-15min": {
        "task": "tasks.scrape_kroger_task",
        "schedule": 900.0,
    },
    "scrape-aldi-every-15min": {
        "task": "tasks.scrape_aldi_task",
        "schedule": 900.0,
    },
}


@app.task(name="tasks.scrape_kroger_task", bind=True, max_retries=3)
def scrape_kroger_task(self):
    try:
        results = scrape_kroger()
        save_price_observations(results)
        return f"Saved {len(results)} prices from Kroger"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@app.task(name="tasks.scrape_aldi_task", bind=True, max_retries=3)
def scrape_aldi_task(self):
    try:
        results = asyncio.run(scrape_aldi())
        save_price_observations(results)
        return f"Saved {len(results)} prices from Aldi"
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))
