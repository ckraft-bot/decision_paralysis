# import config
# from dotenv import load_dotenv
import os
import pandas as pd
import random
import smtplib
import ssl
import mimetypes
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ics import Calendar, Event
from datetime import datetime, timedelta
from fractions import Fraction
import re
import logging

# Constants
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SUBJECT = "Weekly Meal Plan"

COOK_OPTIONS = [
    'Bibimbab',
    'Buddha bowl',
    #'Eggplant parmesan',  # too long of a prep time
    'Frances Cabbage',
    'Fruit smoothie',
    'Gamja Bokkeum',
    'Gyeran mari',
    # 'Japchae',  # too long of a prep time
    'Kimchi jjigae',
    'Kimchi fried rice',
    'Kimbap bowl',
    'Mandoo',
    'Omurice',
    'Pad woon sen',
    'Pajun',
    'Rice & seaweed',
    'Shrimp tacos',
    'Spicy ramen',
    'Tilapia & baked vegetables',
    'Tofu jorim',
    'Tomato and egg',
    'Yangzhou fried rice',
    'Yangchun noodles',
]

INGREDIENTS = {
    "Bibimbab": {
        "Rice": [
            "3 cups short grain rice"
        ],
        "Meat": [
            "8 ounces thinly sliced tender beef (rib eye, sirloin, etc. or ground beef)",
            "1½ tablespoons soy sauce",
            "2 teaspoons sugar",
            "2 teaspoons sesame oil",
            "2 teaspoons rice wine",
            "1 teaspoon minced garlic",
            "1 tablespoon chopped scallion",
            "pepper to taste"
        ],
        "Vegetables and Eggs": [
            "8 ounces mung bean sprouts (sukju, 숙주) or soybean sprouts (kongnamul, 콩나물)",
            "1 bunch spinach, about 8 ounces",
            "2 small cucumbers, about 5 ounces",
            "4 ounces mushrooms (shiitake, white, cremini, etc.)",
            "2 medium carrots, about 5 ounces",
            "1 ½ teaspoons minced garlic, divided",
            "3 tablespoons chopped scallion, divided",
            "sesame oil",
            "sesame seeds",
            "salt",
            "4 eggs - optional",
            "cooking oil"
        ],
        "More Vegetable Options": [
            "8 ounces Kongnamul (soybean sprouts)",
            "10 ounces mu (Korean radish)"
        ],
        "Bibimbap Sauce": [
            "4 tablespoons gochujang",
            "2 teaspoons sugar - adjust to taste, 1-3 teaspoons",
            "1 tablespoon sesame oil",
            "1 tablespoon water"
        ]
    },
    "Buddha bowl": {
        "Bowl": [
            "2 cups cooked rice",
            "1 avocado",
            "2 red bell peppers",
            "3 cups chopped kale",
            "4 green onions chopped",
            "1 tablespoon olive oil",
            "Optional: chopped peanuts for garnish"
        ],
        "Tofu": [
            "1 block extra firm tofu",
            "1 tablespoon low sodium tamari or soy sauce",
            "1 teaspoon toasted sesame oil",
            "1 tablespoon maple syrup or honey",
            "2 tablespoons corn starch",
            "2 tablespoons gluten free plain breadcrumbs or regular",
            "½ cup peanut sauce"
        ]
    },
    "Frances Cabbage": {
        "Main Ingredients": [
            "1 head of cabbage",
            "1 garlic clove",
            "cheese",
            "bacon bits",
            "1 tablespoon olive oil",
            "salt",
            "pepper",
        ]
    },
    "Gamja Bokkeum": {
        "Main Ingredients": [
            "2 medium Yukon potatoes or 1 large russet potato",
            "1 tablespoon oil",
            "1 clove garlic, minced",
            "½ small onion, thinly sliced",
            "½ small carrot, thinly sliced",
            "2 green onions, thinly sliced",
            "Salt to taste",
            "Pepper to taste",
            "2 teaspoons toasted sesame seeds"
        ]
    },
    "Gyeran mari": {
        "Main Ingredients": [
            "4 - 5 large eggs",
            "1 cup anchovy broth (or water or dashima broth) adjust to taste",
            "1½ teaspoons salted shrimp (saeujeot) or 3/4 teaspoon salt (or fish sauce)",
            "2 tablespoons chopped scallion",
            "1 teaspoon sesame oil, divided - optional",
            "½ teaspoon sesame seeds - optional"
        ]
    },
    "Japchae": {
        "Main Ingredients": [
            "7 ounces Korean potato starch noodles (dangmyeon, 당면)",
            "1 carrot (about 3 ounces)",
            "½ medium onion (preferably sweet variety, 4 to 5 ounces)",
            "2 scallions",
            "4 ounces lean tender beef (sirloin, chuck tender, rib eye, etc.) or pork loin",
            "3 - 4 ounces fresh shiitake mushrooms (or 4 to 5 dried shiitake, soaked until plump)",
            "6 ounces fresh spinach (preferably a bunch of spinach)",
            "oil for stir frying",
            "salt",
            "egg garnish (jidan) - optional"
        ],
        "Sauce": [
            "3½ tablespoons soy sauce",
            "3 tablespoons sugar (or brown sugar, you can use a little less if you want)",
            "2 tablespoons sesame oil",
            "2 teaspoons minced garlic",
            "1 tablespoon roasted sesame seeds",
            "black pepper to taste"
        ]
    },
    "Kimchi jjigae": {
        "Main Ingredients": [
            "2 cups packed bite size kimchi fully fermented",
            "4 ounces fresh pork belly or other pork meat with some fat or other protein choice",
            "1 to 3 teaspoons gochugaru - adjust to taste or omit",
            "1 teaspoon minced garlic",
            "1 tablespoon cooking oil",
            "½ cup juice from kimchi if available",
            "6 ounces tofu",
            "2 scallions",
            "salt (or a little bit of soup soy sauce or regular soy sauce) and pepper to taste"
        ]
    },
    "Kimchi fried rice": {
        "Main Ingredients": [
            "3 tablespoons unsalted butter",
            "½ small onion, medium dice",
            "1 cup roughly chopped kimchi (6 ounces)",
            "2 tablespoons kimchi juice, or to taste",
            "½ cup small-dice Spam, ham or leftover cooked meat",
            "2 cups cooked, cooled rice (preferably short-grain)",
            "2 teaspoons soy sauce, or to taste",
            "1 teaspoon sesame oil, or to taste",
            "2 teaspoons vegetable oil",
            "2 eggs",
            "Salt to taste",
            "Crumbled or slivered nori (roasted seaweed) for garnish"
        ]
    },
    "Kimbap bowl": {
        "Main Ingredients": [
            "4 gim, dried seaweed aka nori",
            "cooking oil"
        ],
        "For the Rice": [
            "1½ cups uncooked short grain rice (standard measuring cup not the cup that comes with a rice cooker)",
            "1 tablespoon sesame oil",
            "salt to taste (about ½ teaspoon) start with a little less"
        ],
        "For the Beef": [
            "8 ounces lean tender beef, cut into thin strips (or bulgogi meat or ground beef)",
            "2 teaspoons soy sauce",
            "1 teaspoon rice wine (or mirin)",
            "1 teaspoon sugar",
            "1 teaspoon sesame oil",
            "½ teaspoon minced garlic"
        ],
        "For the Vegetables": [
            "1 bunch spinach, about 8 ounces",
            "1 teaspoon sesame oil",
            "salt to taste - about 1/4 teaspoon",
            "2 medium carrots, julienned (or ½-inch thick long strips)",
            "4 strips pre-cut pickled radish (danmuji, 단무지) strips, white or yellow if not pre-cut, cut into about ½-inch thick long strips",
            "4 strips prepared burdock roots (ueong, 우엉) Or make braised burdock roots"
        ],
        "For the Egg": [
            "2 large eggs"
        ],
        "For the Fish Cake": [
            "1 or 2 (if small) sheets fish cake - eomuk (어묵)",
            "1 teaspoon soy sauce",
            "½ teaspoon sugar",
            "½ teaspoon sesame oil"
        ]
    },
    "Omurice": {
        "Main Ingredients": [
            "½ medium onion finely chopped",
            "1 scallion finely chopped",
            "1 small carrot finely chopped",
            "4 ounces beef or pork, chicken or shrimp, ground or finely chopped",
            "1 tablespoon soy sauce",
            "1½ tablespoon ketchup adjust to taste, and more for decoration",
            "salt and pepper",
            "Oil for pan frying",
            "2 servings of cooked rice",
            "4 eggs"
        ]
    },
    "Pajun": {
        "Main Ingredients": [
            "2 cups all-purpose flour",
            "2 large eggs, beaten",
            "1 teaspoon kosher salt",
            "1 bunch scallions, green and white parts; halved lengthwise and cut into 2- to 3-inch lengths",
            "1½ cups water",
            "1½ tablespoons vegetable oil, for frying",
            "Soy sauce, or spicy dipping sauce, for serving"
        ]
    },
    "Shrimp tacos": {
        "Main Ingredients": [
            "2 pounds large frozen peeled and deveined shrimp, thawed",
            "1½ teaspoons chili powder",
            "1 teaspoon freshly minced garlic",
            "½ teaspoon paprika",
            "½ teaspoon ground cumin",
            "½ teaspoon salt",
            "½ teaspoon ground black pepper",
            "¼ teaspoon ground coriander",
            "¼ teaspoon grated Valencia orange zest",
            "2 tablespoons olive oil, or more as needed",
            "2 tablespoons sour cream",
            "1 teaspoon of lemon juice",
            "1 teaspoon chopped fresh cilantro",
            "¼ teaspoon garlic powder",
            "1 pinch salt and ground black pepper",
            "20 (6 inch) corn tortillas",
            "2 avocados, thinly sliced, or to taste",
            "1 red onion, finely diced, or to taste",
            "½ bunch fresh cilantro, chopped, or to taste",
            "1 jalapeño pepper, diced, or to taste (Optional)",
            "2 limes, cut into wedges, or as needed"
        ]
    },
    "Spicy ramen": {
        "Main Ingredients": [
            "2 Beef Steaks, cubed",
            "Salt and Pepper",
            "2 teaspoon Sesame Oil",
            "3 tablespoons Kimchee Base or Gochujang Sauce",
            "2 tablespoons Soy Sauce",
            "¼ cup Scallions, chopped",
            "1½ cups Water",
            "1 Package Instant Ramen noodles",
            "Black sesame seeds"
        ]
    },
    "Tilapia & baked vegetables": {
        "Main Ingredients": [
            "Frozen tilapia",
            "Mixed vegetables of your choice",
            "2 tablespoon olive oil",
            "1½ teaspoon Italian seasoning",
            "2 - 3 cloves garlic, minced",
            "Salt and freshly ground black pepper",
            "1 cup grape tomatoes (optional)",
            "1 tablespoon fresh lemon juice"
        ]
    },
    "Tofu jorim": {
        "Main Ingredients": [
            "1 about 18-oz pack firm tofu",
            "1 tablespoon vegetable/canola oil"
        ],
        "For the Sauce": [
            "3 tablespoons soy sauce",
            "3 tablespoons water",
            "1 tablespoon sesame oil",
            "1 teaspoon sugar",
            "1 teaspoon Korean red pepper flakes (gochugaru)",
            "1 teaspoon sesame seed",
            "1 teaspoon minced garlic",
            "2 scallions (1 if large), finely chopped about 1/4 cup"
        ]
    },
    "Yangzhou fried rice": {
        "Main Ingredients": [
            "5 cups cooked white rice (about 2 cups uncooked; preferably made the day before and refrigerated)",
            "3 tablespoons cooking oil",
            "2 carrots (diced)",
            "1/3 cup peas (frozen or fresh)",
            "10 shrimp (deveined, deshelled, no tail; cut into small pieces)",
            "3 eggs",
            "½ cup char siu pork (or Chinese sausage; cut into small pieces)",
            "2 scallions (chopped)",
            "1½ tablespoons soy sauce",
            "Pepper (to taste)",
            "Salt (to taste)"
        ]
    },
    "Yangchun noodles": {
        "Main Ingredients": [
            "100 grams noodles",
            "1 tablespoon soy sauce, or to taste",
            "1 teaspoon home rendered lard, or ½ teaspoon sesame oil",
            "1/4 teaspoon sugar",
            "1 green onion, finely chopped",
            "2 cups Light chicken stock, or liquid for cooking the noodles as needed"
        ]
    },
}

ORDER_OUT_OPTIONS = [
    'Order out Chinese',
    'Order out Fast food',
    'Order out Indian',
    'Order out Italian',
    'Order out Japanese',
    'Order out Korean',
    'Order out Mexican',
    'Order out Thai',
]

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


# -- Parsing Helpers --
UNIT_MAP = {
    'teaspoon': 'teaspoon', 
    'teaspoons': 'teaspoon', 
    'tablespoon': 'tablespoon', 
    'tablespoons': 'tablespoon', 
    'cup': 'cup', 
    'cups': 'cup',
    'g': 'gram',
    'grams': 'gram',
    'oz': 'ounce',  
}

def parse_ingredient(line):
    """
    Parse a line like '2 teaspoon Sesame Oil' into (quantity: float, unit: str, item: str).
    Returns (None, None, original_line) if no match.
    """
    match = re.match(r"^([\d\s\/\.]+)\s*([A-Za-z\.]+)\s+(.+)$", line)
    if not match:
        return None, None, line
    qty_str, unit_raw, item = match.groups()
    # parse quantity (including fractions)
    try:
        qty = float(sum(Fraction(s) for s in qty_str.split()))
    except Exception:
        return None, None, line
    unit_norm = UNIT_MAP.get(unit_raw.lower(), unit_raw.lower())
    item_norm = item.strip().lower()
    return qty, unit_norm, item_norm

# -- Core Functions --

def format_ingredients(ingredients):
    if isinstance(ingredients, dict):
        return "\n\n".join([
            f"**{section}**:\n" + "\n".join([f"- {item}" for item in items])
            for section, items in ingredients.items()
        ])
    return ingredients


def generate_meal_plan_dict():
    order_out_day = random.choice(DAYS_OF_WEEK)
    meal_plan = {
        day: random.choice(ORDER_OUT_OPTIONS) if day == order_out_day else random.choice(COOK_OPTIONS)
        for day in DAYS_OF_WEEK
    }
    return {
        day: {
            "Meal": meal,
            "Ingredients": format_ingredients(INGREDIENTS.get(meal, {}))
        }
        for day, meal in meal_plan.items()
    }


def aggregate_ingredients(meal_plan_dict):
    """
    Aggregate raw ingredients into summed quantities per item+unit.
    Returns dict mapping item -> {unit: total_qty} or list of lines for non-parsable.
    """
    totals = {}
    others = []
    for details in meal_plan_dict.values():
        raw = INGREDIENTS.get(details['Meal'])
        if isinstance(raw, dict):
            for section_items in raw.values():
                for line in section_items:
                    qty, unit, item = parse_ingredient(line)
                    if qty is not None:
                        key = item
                        totals.setdefault(key, {}).setdefault(unit, 0)
                        totals[key][unit] += qty
                    else:
                        others.append(line)
    # Format totals back to strings
    agg = {}
    for item, unit_dict in totals.items():
        agg[item] = [f"{unit_dict[unit]} {unit} {item}" for unit in unit_dict]
    if others:
        agg['misc'] = others
    return agg


def get_next_week_monday(start_from=None):
    if start_from is None:
        start_from = datetime.today().date()
    current_monday = start_from - timedelta(days=start_from.weekday())
    return current_monday + timedelta(days=7)


def generate_ical(meal_plan_with_ingredients, start_date=None):
    if start_date is None:
        start_date = get_next_week_monday()
    cal = Calendar()
    for idx, day in enumerate(DAYS_OF_WEEK):
        date = start_date + timedelta(days=idx)
        details = meal_plan_with_ingredients.get(day, {})
        evt = Event()
        evt.name = f"{day}: {details.get('Meal')}"
        evt.begin = date.isoformat()
        evt.make_all_day()
        evt.description = f"Meal: {details.get('Meal')}\n\nIngredients:\n{details.get('Ingredients')}"
        cal.events.add(evt)
    filename = 'meal_plan.ics'
    with open(filename, 'w') as f:
        f.writelines(cal)
    return filename


def send_email(meal_plan_text, shopping_list, ical_filename):
    EMAIL_USERNAME = os.environ.get('email_username')
    EMAIL_PASSWORD = os.environ.get('email_password')
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        raise ValueError("Email credentials missing.")
    # Build shopping list HTML
    shop_html = '<h3>Aggregated Shopping List:</h3><ul>'
    for item, lines in shopping_list.items():
        shop_html += f'<li><strong>{item.title()}:</strong><ul>'
        for line in lines:
            shop_html += f'<li>{line}</li>'
        shop_html += '</ul></li>'
    shop_html += '</ul>'
    body = f"""
    <html><body>
        <p>Here is your weekly meal plan:</p>
        <pre>{meal_plan_text}</pre>
        {shop_html}
        <p>Attached calendar: {ical_filename}</p>
    </body></html>
    """
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = EMAIL_USERNAME
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body, 'html'))
    # attach ical
    with open(ical_filename, 'rb') as f:
        data = f.read()
    mtype, _ = mimetypes.guess_type(ical_filename)
    maint, sub = mtype.split('/') if mtype else ('application','octet-stream')
    part = MIMEBase(maint, sub)
    part.set_payload(data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{ical_filename}"')
    msg.attach(part)
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()) as s:
        s.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        s.sendmail(EMAIL_USERNAME, EMAIL_USERNAME, msg.as_string())


def main():
    plan = generate_meal_plan_dict()
    plan_text = '\n\n'.join(f"{day}: {v['Meal']}" for day,v in plan.items())
    aggregated = aggregate_ingredients(plan)
    ics = generate_ical(plan)
    send_email(plan_text, aggregated, ics)

if __name__ == '__main__':
    main()
