import os
import base64
import requests

CLIENT_ID     = os.getenv("KROGER_CLIENT_ID")
CLIENT_SECRET = os.getenv("KROGER_CLIENT_SECRET")
LOCATION_ID   = os.getenv("KROGER_LOCATION_ID", "")

SEARCH_TERMS = [
    "chicken breast",
    "eggs",
    "whole milk",
    "bread",
    "rice",
    "pasta",
    "butter",
    "bananas",
]

def find_location_id(token: str, zip_code: str) -> str:
    response = requests.get(
        "https://api.kroger.com/v1/locations",
        headers={"Authorization": f"Bearer {token}"},
        params={"filter.zipCode.near": zip_code, "filter.limit": 1}
    )
    response.raise_for_status()
    locations = response.json().get("data", [])
    if not locations:
        raise ValueError(f"No Kroger locations found near zip {zip_code}")
    loc = locations[0]
    print(f"[kroger] Using location: {loc.get('name')} ({loc.get('locationId')})")
    return loc["locationId"]

def get_token() -> str:
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    response = requests.post(
        "https://api.kroger.com/v1/connect/oauth2/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {credentials}"
        },
        data="grant_type=client_credentials&scope=product.compact"
    )
    response.raise_for_status()
    return response.json()["access_token"]

def scrape_kroger(zip_code: str = os.getenv("KROGER_ZIP_CODE", "10001")) -> list[dict]:
    token = get_token()
    location_id = LOCATION_ID or find_location_id(token, zip_code)
    results = []

    for term in SEARCH_TERMS:
        try:
            response = requests.get(
                "https://api.kroger.com/v1/products",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "filter.term": term,
                    "filter.locationId": location_id,
                    "filter.limit": 10
                }
            )
            response.raise_for_status()
            body = response.json()
            products = body.get("data", [])
            print(f"[kroger] '{term}': {len(products)} products, raw sample: {str(body)[:300]}")

            for product in products:
                try:
                    name  = product.get("description", "")
                    brand = product.get("brand", "")
                    items = product.get("items", [])

                    if not items:
                        continue

                    price_info = items[0].get("price", {})
                    price = price_info.get("promo") or price_info.get("regular")

                    if price and name:
                        results.append({
                            "store": "kroger",
                            "name": f"{brand} {name}".strip(),
                            "price": float(price),
                        })
                except Exception as e:
                    print(f"[kroger] Error parsing product: {e}")
                    continue

        except Exception as e:
            print(f"[kroger] Failed on term '{term}': {e}")
            continue

    return results
