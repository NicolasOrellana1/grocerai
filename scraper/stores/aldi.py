import asyncio
import random
from playwright.async_api import async_playwright

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/123.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/122.0 Safari/537.36",
]

SEARCH_URLS = [
    "https://www.aldi.us/en/search/?text=chicken+breast",
    "https://www.aldi.us/en/search/?text=eggs",
    "https://www.aldi.us/en/search/?text=milk",
]


async def scrape_aldi() -> list[dict]:
    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )
        context = await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1280, "height": 800},
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )
        page = await context.new_page()

        for url in SEARCH_URLS:
            try:
                await asyncio.sleep(random.uniform(2.0, 5.0))
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_selector('[class*="product-tile"]', timeout=15000)

                tiles = await page.query_selector_all('[class*="product-tile"]')
                for tile in tiles[:10]:
                    try:
                        name_el = await tile.query_selector('[class*="product-tile__name"]')
                        price_el = await tile.query_selector('[class*="product-tile__price"]')

                        if not name_el or not price_el:
                            continue

                        name = (await name_el.inner_text()).strip()
                        price_text = (await price_el.inner_text()).strip()
                        price_clean = price_text.replace("$", "").replace("\n", "").strip().split()[0]
                        price = float(price_clean)

                        results.append({
                            "store": "aldi",
                            "name": name,
                            "price": price,
                        })
                    except Exception as e:
                        print(f"[aldi] Error parsing tile: {e}")
                        continue

            except Exception as e:
                print(f"[aldi] Failed on {url}: {e}")
                continue

        await browser.close()

    return results
