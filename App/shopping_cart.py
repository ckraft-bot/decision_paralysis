import os
import time
import json
import requests
from urllib.parse import urlencode
import meal_planner_email  # your meal plan dict from the previous step
from meal_planner_email import meal_plan_dict, INGREDIENTS

# ── CONFIG ──
WALMART_USERNAME = os.getenv("walmart_username") # Added to repository secrets --> settings > secrets >actions
WALMART_PASSWORD = os.getenv("walmart_password") # Added to repository secrets --> settings > secrets >actions
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"  # mimic a real browser
SEARCH_API = "https://www.walmart.com/search/api/preso?{}"
CART_API   = "https://www.walmart.com/cart/api/v2/cart/add"  # unofficial endpoint

session = requests.Session()
session.headers.update({
    "User-Agent": USER_AGENT,
    "Accept": "application/json, text/plain, */*",
})

def login():
    """
    Perform a form POST to Walmart's identity endpoint to authenticate.
    You may need to fetch a CSRF token first from https://www.walmart.com/account
    """
    # 1) GET the login page to grab csrf token
    r = session.get("https://www.walmart.com/account/login")
    r.raise_for_status()
    # extract a token (e.g., name="csrf" value="...")—simplest with regex
    import re
    m = re.search(r'name="csrf" value="(?P<token>[^"]+)"', r.text)
    csrf = m.group("token") if m else ""

    payload = {
        "email": WALMART_USERNAME,
        "password": WALMART_PASSWORD,
        "csrf": csrf,
    }
    # 2) POST credentials
    r2 = session.post("https://www.walmart.com/account/login", data=payload)
    r2.raise_for_status()
    if "My Account" not in r2.text:
        raise RuntimeError("Login failed")
    print("✅ Logged in to Walmart.com")

def search_product(query):
    """
    Use Walmart’s JSON search API to find a productId for a given query.
    Returns the first productId found.
    """
    params = {"query": query, "cat_id": "0", "start": 0}
    url = SEARCH_API.format(urlencode(params))
    r = session.get(url)
    r.raise_for_status()
    data = r.json()
    # traverse JSON to find the first item:
    try:
        item = data["presoItems"][0]["product"]
        return item["productId"], item.get("primaryOfferId")
    except Exception:
        print(f"⚠️ No results for '{query}'")
        return None, None

def add_to_cart(product_id, offer_id=None, quantity=1):
    """
    POST to Walmart’s cart API to add one unit of product_id.
    """
    payload = {
        "productId": product_id,
        "quantity": quantity,
    }
    if offer_id:
        payload["offerId"] = offer_id
    headers = {
        "Content-Type": "application/json",
        "Referer": "https://www.walmart.com/cart",
    }
    r = session.post(CART_API, headers=headers, data=json.dumps(payload))
    if r.status_code == 200 and r.json().get("status") == "SUCCESS":
        print(f"➕ Added product {product_id} to cart")
    else:
        print(f"❌ Failed to add {product_id}: {r.status_code} {r.text[:200]}")

def build_shopping_list(plan_dict):
    """
    Flatten your meal_plan_dict’s INGREDIENTS sections
    into a de-duplicated list of search queries.
    """
    from itertools import chain
    items = []
    for details in plan_dict.values():
        meal = details["Meal"]
        # use your original INGREDIENTS dict, not the HTML-formatted one
        ing = INGREDIENTS.get(meal, {})
        for section_items in ing.values():
            items.extend(section_items)
    # dedupe and return
    return sorted(set(items))

if __name__ == "__main__":
    # 1) login once
    login()

    # 2) build your list from the same INGREDIENTS dict you already have
    shopping_queries = build_shopping_list(meal_plan_dict)

    # 3) for each query: search → add to cart
    for q in shopping_queries:
        pid, oid = search_product(q)
        if pid:
            add_to_cart(pid, oid)
            time.sleep(0.5)  # be polite
