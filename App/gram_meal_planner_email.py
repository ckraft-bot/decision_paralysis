# import config
# from dotenv import load_dotenv
import os
import pandas as pd
import random
import smtplib
import ssl
import mimetypes
import logging
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ics import Calendar, Event
from datetime import datetime, timedelta

# Logging configuration
logging.basicConfig(
    level=logging.INFO,  # change to DEBUG for more verbosity
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Constants
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SUBJECT = "Weekly Meal Plan"

COOK_OPTIONS = [
    "Egg salad sandwiches",
    "Chicken noodle soup",
    "Tomato soup with grilled cheese",
    "Lasagna",
    "Spaghetti",
    "Omelets with cheese and vegetables",
    "Pancakes with fruit",
    "French toast",
    "Biscuits and gravy",
]


INGREDIENTS = {
    "Egg salad sandwiches": {
        "Main Ingredients": [
            "6 eggs",
            "1/4 cup mayonnaise",
            "1 teaspoon mustard",
            "2 tablespoons celery (finely chopped)",
            "Salt and black pepper to taste",
            "8 slices sandwich bread",
            "Lettuce leaves (optional)"
        ]
    },

    "Chicken noodle soup": {
        "Main Ingredients": [
            "2 cups cooked chicken (shredded)",
            "6 cups chicken broth",
            "2 carrots (sliced)",
            "2 celery stalks (sliced)",
            "1 small onion (chopped)",
            "2 cups egg noodles",
            "2 cloves garlic (minced)",
            "Salt and pepper to taste",
            "1 teaspoon dried thyme"
        ]
    },

    "Tomato soup with grilled cheese": {
        "Main Ingredients": [
            "1 can crushed tomatoes (28 oz)",
            "2 cups vegetable or chicken broth",
            "1/2 cup heavy cream or milk",
            "1 tablespoon butter",
            "1 small onion (chopped)",
            "1 teaspoon sugar",
            "Salt and pepper to taste",
            "8 slices bread",
            "4 slices cheddar cheese",
            "2 tablespoons butter (for grilling)"
        ]
    },

    "Lasagna": {
        "Main Ingredients": [
            "12 lasagna noodles",
            "1 pound ground beef or Italian sausage",
            "3 cups marinara sauce",
            "2 cups ricotta cheese",
            "2 cups shredded mozzarella",
            "1/2 cup grated parmesan",
            "1 egg",
            "2 teaspoons Italian seasoning",
            "Salt and pepper to taste"
        ]
    },

    "Spaghetti": {
        "Main Ingredients": [
            "12 oz spaghetti pasta",
            "3 cups marinara sauce",
            "1 pound ground beef (optional)",
            "2 cloves garlic (minced)",
            "1 tablespoon olive oil",
            "Salt and pepper to taste",
            "Grated parmesan cheese"
        ]
    },

    "Omelets with cheese and vegetables": {
        "Main Ingredients": [
            "6 eggs",
            "1/4 cup milk",
            "1/2 cup shredded cheese",
            "1/2 cup bell peppers (diced)",
            "1/4 cup onions (diced)",
            "1/2 cup mushrooms (sliced)",
            "1 tablespoon butter",
            "Salt and pepper to taste"
        ]
    },

    "Pancakes with fruit": {
        "Main Ingredients": [
            "1 cup all-purpose flour",
            "1 tablespoon sugar",
            "1 teaspoon baking powder",
            "1 egg",
            "1 cup milk",
            "2 tablespoons melted butter",
            "1 teaspoon vanilla extract",
            "1 cup fresh fruit (berries or sliced bananas)",
            "Maple syrup"
        ]
    },

    "French toast": {
        "Main Ingredients": [
            "8 slices bread",
            "3 eggs",
            "1 cup milk",
            "1 teaspoon cinnamon",
            "1 teaspoon vanilla extract",
            "2 tablespoons butter",
            "Maple syrup",
            "Powdered sugar (optional)"
        ]
    },

    "Biscuits and gravy": {
        "Main Ingredients": [
            "8 refrigerated or homemade biscuits",
            "1/2 pound breakfast sausage",
            "3 tablespoons flour",
            "2 cups milk",
            "Salt and black pepper to taste"
        ]
    }
}


ORDER_OUT_OPTIONS = [
    'Order out fast food',
    'Order out pizza',
    'Order out Mexican'
]

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']



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
            "Suggested Ingredients": format_ingredients_html(INGREDIENTS.get(meal, "Order out or ingredients not available"))
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


def format_ingredients_html(ingredients):
    """Format ingredients as plain text for calendar descriptions."""
    if isinstance(ingredients, dict):
        return "\n\n".join([
            f"{section.upper()}:\n" + "\n".join([f"- {item}" for item in items])
            for section, items in ingredients.items()
        ])
    
    # Fallback for string input
    return ingredients.replace("<br>", "\n").replace("&bull;", "-").replace("&nbsp;", " ").strip()


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
        ingredients = details.get("Suggested Ingredients", "")
        
        event = Event()
        event.name = f"{day}: {meal}"
        event.begin = event_date.isoformat()
        event.make_all_day()
        formatted_ingredients = format_ingredients_html(ingredients)
        event.description = f"Meal 🍽️: {meal}\n\nIngredients 🛒:\n\n{formatted_ingredients}"
        cal.events.add(event)
    
    ics_filename = "meal_plan.ics"
    with open(ics_filename, 'w', encoding='utf-8') as my_file:
    # with open(ics_filename, 'w') as my_file:
        my_file.writelines(cal)
    
    #print(f"iCal file '{ics_filename}' generated successfully!")
    logger.info("Generated iCal file %s", ics_filename)

    return ics_filename


def send_email(meal_plan, ical_filename):
    """Send the meal plan via email with the iCal file attached."""
    EMAIL_USERNAME = os.environ['email_username']
    EMAIL_PASSWORD = os.environ['email_password']

    GRAM_EMAIL = os.environ['gram_email']

    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        raise ValueError("Email credentials not found. Ensure they are set properly in GitHub Actions.")

    receiver_email = GRAM_EMAIL  # or set to a different recipient if desired
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
            logger.info("Email sent to %s", receiver_email)
        # print(f"Email sent to {receiver_email}")
    except smtplib.SMTPException as e:
        logger.error("Failed to send email: %s", e, exc_info=True)
        # print(f"Failed to send email: {e}")


def main():
    logger.info("Starting meal-plan generation")
    meal_plan_dict = generate_meal_plan_dict()
    logger.debug("Meal plan dict: %s", meal_plan_dict)

    meal_plan_output = "\n\n".join(
        f"<strong>{day}</strong>:\nMeal: {details['Meal']}\nSuggested Ingredients:\n{details['Suggested Ingredients']}"
        for day, details in meal_plan_dict.items()
    )

    ical_filename = generate_ical(meal_plan_dict)
    logger.debug("iCal filename: %s", ical_filename)

    send_email(meal_plan_output, ical_filename)
    logger.info("Finished sending meal-plan email to gram")


if __name__ == "__main__":
    main()