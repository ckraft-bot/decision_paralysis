import os
import time
import json
import re
import requests
from urllib.parse import urlencode
import meal_planner_email  # your meal plan dict from the previous step
from meal_planner_email import meal_plan_dict, INGREDIENTS
import logging

# ——— Logging setup ———
logging.basicConfig(
    level=logging.DEBUG,  # or DEBUG for even more detail
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# ── CONFIG ──
# WALMART_USERNAME = os.getenv("walmart_username") # Added to repository secrets --> settings > secrets >actions
# WALMART_PASSWORD = os.getenv("walmart_password") # Added to repository secrets --> settings > secrets >actions

WALMART_USERNAME = ''
WALMART_PASSWORD = ''
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
    logger.info("✅ Logged in to Walmart.com")

def search_product(query):
    logger.debug("Searching for product: %s", query)
    params = {"query": query, "cat_id": "0", "start": 0}
    url = SEARCH_API.format(urlencode(params))
    r = session.get(url)
    r.raise_for_status()
    data = r.json()
    try:
        item = data["presoItems"][0]["product"]
        pid, oid = item["productId"], item.get("primaryOfferId")
        logger.info("Found product %s (offer %s) for query '%s'", pid, oid, query)
        return pid, oid
    except Exception:
        logger.warning("No search results for '%s'", query)
        return None, None

def add_to_cart(product_id, offer_id=None, quantity=1):
    logger.info("Adding to cart: product_id=%s, offer_id=%s, qty=%d",
                product_id, offer_id, quantity)
    payload = {"productId": product_id, "quantity": quantity}
    if offer_id:
        payload["offerId"] = offer_id
    headers = {"Content-Type": "application/json", "Referer": "https://www.walmart.com/cart"}
    r = session.post(CART_API, headers=headers, data=json.dumps(payload))

    if r.status_code == 200 and r.json().get("status") == "SUCCESS":
        logger.info("➕ Added product %s to cart", product_id)
    else:
        logger.error("❌ Failed to add %s: %s %s", product_id, r.status_code, r.text[:200])

def build_shopping_list(plan_dict):
    logger.debug("Building shopping list from meal plan")
    items = []
    for details in plan_dict.values():
        meal = details["Meal"]
        ing = INGREDIENTS.get(meal, {})
        for section_items in ing.values():
            items.extend(section_items)
    shopping_list = sorted(set(items))
    logger.info("Shopping list contains %d unique items", len(shopping_list))
    return shopping_list

if __name__ == "__main__":
    logger.info("=== Walmart-Cart Automation Started ===")
    try:
        login()
        shopping_queries = build_shopping_list(meal_plan_dict)
        for q in shopping_queries:
            pid, oid = search_product(q)
            if pid:
                add_to_cart(pid, oid)
                time.sleep(0.5)
    except Exception as e:
        logger.exception("Script terminated with an error")
    else:
        logger.info("=== Completed adding all items to cart ===")