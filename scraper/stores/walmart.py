import asyncio
import random
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
]

SEARCH_URLS = [
    "https://www.walmart.com/search?q=chicken+breast",
    "https://www.walmart.com/search?q=eggs+dozen",
    "https://www.walmart.com/search?q=whole+milk+gallon",
]

async def scrape_walmart() -> list[dict]:
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"]
        )

        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 800},
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"}
        )

        page = await context.new_page()

        for url in SEARCH_URLS:
            try:
                await asyncio.sleep(random.uniform(2.0, 5.0))
                await page.goto(url, wait_until="networkidle", timeout=30000)

                # Wait for the updated product tile container
                await page.wait_for_selector(
                    '[data-test-id="gpt-product-tile-grid-container"]',
                    timeout=15000
                )

                items = await page.query_selector_all(
                    '[data-test-id="gpt-product-tile-grid-container"]'
                )

                for item in items[:10]:
                    try:
                        name_el  = await item.query_selector('[data-automation-id="product-title"]')
                        price_el = await item.query_selector('[data-automation-id="product-price"]')

                        if not name_el or not price_el:
                            continue

                        name = await name_el.inner_text()

                        # Price lives in nested spans — grab the full text and clean it
                        price_text = await price_el.inner_text()
                        # price_text looks like "$15\n36" or "$15.36" — normalize it
                        price_clean = price_text.replace("\n", ".").replace("$", "").strip()
                        # Take just the first price if multiple exist
                        price_value = float(price_clean.split()[0])

                        results.append({
                            "store": "walmart",
                            "name": name.strip(),
                            "price": price_value,
                        })

                    except Exception as e:
                        print(f"[walmart] Error parsing item: {e}")
                        continue

            except Exception as e:
                print(f"[walmart] Failed on {url}: {e}")
                continue

        await browser.close()

    return results