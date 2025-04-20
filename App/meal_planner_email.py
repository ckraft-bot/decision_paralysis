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
            "1 ½ tablespoons soy sauce",
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
            "1 tsp toasted sesame oil",
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
            "1 tbsp oil",
            "1 clove garlic, minced",
            "½ small onion, thinly sliced",
            "½ small carrot, thinly sliced",
            "2 green onions, thinly sliced",
            "Salt to taste",
            "Pepper to taste",
            "2 tsp toasted sesame seeds"
        ]
    },
    "Gyeran mari": {
        "Main Ingredients": [
            "4 - 5 large eggs",
            "1 cup anchovy broth (or water or dashima broth) adjust to taste",
            "1 ½ teaspoons salted shrimp (saeujeot) or 3/4 teaspoon salt (or fish sauce)",
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
            "3 to 4 ounces fresh shiitake mushrooms (or 4 to 5 dried shiitake, soaked until plump)",
            "6 ounces fresh spinach (preferably a bunch of spinach)",
            "oil for stir frying",
            "salt",
            "egg garnish (jidan) - optional"
        ],
        "Sauce": [
            "3 ½ tablespoons soy sauce",
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
            "1 to 3 teaspoons gochugaru (Korean red chili pepper flakes) adjust to taste or omit",
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
            "1 ½ cups uncooked short grain rice (standard measuring cup not the cup that comes with a rice cooker)",
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
            "1 ½ tablespoon ketchup adjust to taste, and more for decoration",
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
            "1 ½ cups water",
            "1 ½ tablespoons vegetable oil, for frying",
            "Soy sauce, or spicy dipping sauce, for serving"
        ]
    },
    "Shrimp tacos": {
        "Main Ingredients": [
            "2 pounds large frozen peeled and deveined shrimp, thawed",
            "1 ½ teaspoons chili powder",
            "1 teaspoon freshly minced garlic",
            "½ teaspoon paprika",
            "½ teaspoon ground cumin",
            "½ teaspoon salt",
            "½ teaspoon ground black pepper",
            "¼ teaspoon ground coriander",
            "¼ teaspoon grated Valencia orange zest",
            "2 tablespoons olive oil, or more as needed",
            "2 tablespoons sour cream",
            "1 tsp of lemon juice",
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
            "2 tsp. Sesame Oil",
            "3 tbsp. Kimchee Base or Gochujang Sauce",
            "2 tbsp. Soy Sauce",
            "¼ cup Scallions, chopped",
            "1 ½ Cups Water",
            "1 Package Instant Ramen noodles",
            "Black sesame seeds"
        ]
    },
    "Tilapia & baked vegetables": {
        "Main Ingredients": [
            "Frozen tilapia",
            "Mixed vegetables of your choice",
            "2 Tbsp olive oil",
            "1½ tsp Italian seasoning",
            "2 - 3 cloves garlic, minced",
            "Salt and freshly ground black pepper",
            "1 cup grape tomatoes (optional)",
            "1 Tbsp fresh lemon juice"
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
            "1 ½ tablespoons soy sauce",
            "Pepper (to taste)",
            "Salt (to taste)"
        ]
    },
    "Yangchun noodles": {
        "Main Ingredients": [
            "100 g noodles",
            "1 tbsp. soy sauce, or to taste",
            "1 tsp. home rendered lard, or ½ teaspoon sesame oil",
            "1/4 tsp. sugar",
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


def format_ingredients(ingredients):
    """Format ingredients as bullet points."""
    if isinstance(ingredients, dict):
        return "\n\n".join([
            f"**{section}**:\n" + "\n".join([f"- {item}" for item in items])
            for section, items in ingredients.items()
        ])
    return ingredients


def generate_meal_plan_dict():
    """Generate a weekly meal plan as a dictionary with meals and corresponding ingredients."""
    order_out_day = random.choice(DAYS_OF_WEEK)
    meal_plan = {
        day: random.choice(ORDER_OUT_OPTIONS) if day == order_out_day else random.choice(COOK_OPTIONS)
        for day in DAYS_OF_WEEK
    }
    
    meal_plan_with_ingredients = {
        day: {
            "Meal": meal,
            "Ingredients": format_ingredients(INGREDIENTS.get(meal, "Order out or ingredients not available"))
        }
        for day, meal in meal_plan.items()
    }
    
    return meal_plan_with_ingredients


def get_next_week_monday(start_from=None):
    """
    Returns the date for the Monday of the upcoming week.
    That is, if today is any day of the current week, the function
    returns the Monday of the following week.
    """
    if start_from is None:
        start_from = datetime.today().date()
    
    # Find this week's Monday:
    current_monday = start_from - timedelta(days=start_from.weekday())
    # Next week's Monday is 7 days after this week's Monday:
    next_week_monday = current_monday + timedelta(days=7)
    
    return next_week_monday


def generate_ical(meal_plan_with_ingredients, start_date=None):
    """
    Generates an iCal file from the meal plan.
    meal_plan_with_ingredients: dict from generate_meal_plan_dict.
    start_date: datetime.date object representing the Monday to start the week. 
                Defaults to next week's Monday.
    """
    if start_date is None:
        start_date = get_next_week_monday()
    
    cal = Calendar()
    
    # Map DAYS_OF_WEEK to dates starting from start_date (Monday)
    for idx, day in enumerate(DAYS_OF_WEEK):
        event_date = start_date + timedelta(days=idx)
        details = meal_plan_with_ingredients.get(day, {})
        meal = details.get("Meal", "Meal not set")
        ingredients = details.get("Ingredients", "")
        
        event = Event()
        event.name = f"{day}: {meal}"
        event.begin = event_date.isoformat()
        event.make_all_day()
        event.description = f"Meal: {meal}\n\nIngredients:\n{ingredients}"
        cal.events.add(event)
    
    ics_filename = "meal_plan.ics"
    with open(ics_filename, 'w') as my_file:
        my_file.writelines(cal)
    
    print(f"iCal file '{ics_filename}' generated successfully!")
    return ics_filename


def send_email(meal_plan, ical_filename):
    """Send the meal plan via email with the iCal file attached."""
    EMAIL_USERNAME = os.environ['email_username']
    EMAIL_PASSWORD = os.environ['email_password']

    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        raise ValueError("Email credentials not found. Ensure they are set properly in GitHub Actions.")

    receiver_email = EMAIL_USERNAME  # or set to a different recipient if desired
    body = f"""
    <html>
        <body>
            <p>Here is your weekly meal plan:</p>
            <pre>{meal_plan}</pre>
            <p>The attached calendar file (meal_plan.ics) can be imported into your calendar application.</p>
        </body>
    </html>
    """

    # Create email container and attach HTML body
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USERNAME
    msg['To'] = receiver_email
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body, 'html'))

    # Attach the iCal file
    with open(ical_filename, 'rb') as f:
        ical_data = f.read()
    
    mime_type, _ = mimetypes.guess_type(ical_filename)
    maintype, subtype = mime_type.split('/') if mime_type else ('application', 'octet-stream')
    
    part = MIMEBase(maintype, subtype)
    part.set_payload(ical_data)
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename="{ical_filename}"')
    msg.attach(part)

    # Send the email via SMTP SSL
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()) as server:
            server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
            server.sendmail(EMAIL_USERNAME, receiver_email, msg.as_string())
        print(f"Email sent to {receiver_email}")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")


def main():
    # Generate the meal plan as a dictionary
    meal_plan_dict = generate_meal_plan_dict()
    meal_plan_output = "\n\n".join(
        f"{day}:\nMeal: {details['Meal']}\nIngredients:\n{details['Ingredients']}"
        for day, details in meal_plan_dict.items()
    )
    
    # Generate the iCal file (scheduled for next week's Monday)
    ical_filename = generate_ical(meal_plan_dict)
    
    # Send the email with the meal plan and attached iCal file
    send_email(meal_plan_output, ical_filename)


if __name__ == "__main__":
    main()