import config
import os
import pandas as pd
import random

# Gmail API dependencies
import email
import smtplib
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Constants
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SUBJECT = "Weekly Meal Plan"

# Meal options
COOK_OPTIONS = [
    'Bibimbab', 'Buddha bowl', 'Fruit smoothie', 'Gyeran mari', 
    'Japchae', 'Kimchi Jjigae', 'Kimchi fried rice', 'Kimbap bowl', 
    'Mandoo', 'Omurice', 'Pad woon sen', 'Pajun', 
    'Ramen', 'Shrimp tacos', 'Soy sauce noodles', 'Spicy ramen', 
    'Tilapia & baked vegetables', 'Tofu jorim', 'Tomato and egg', 'rice & seaweed'
]

INGREDIENTS = {
    "Bibimbab": {
        "Rice": [
            "3 cups short grain rice"
        ],
        "Meat": [
            "8 ounces thinly sliced tender beef (rib eye, sirloin, etc. or ground beef)",
            "1.5 tablespoons soy sauce",
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
            "1.5 teaspoons minced garlic, divided",
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
    "Buddha Bowl": {
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
    "Gyeran": {
        "Main Ingredients": [
            "4 - 5 large eggs",
            "1 cup anchovy broth (or water or dashima broth) adjust to taste",
            "1.5 teaspoons salted shrimp (saeujeot) or 3/4 teaspoon salt (or fish sauce)",
            "2 tablespoons chopped scallion",
            "1 teaspoon sesame oil, divided - optional",
            "1/2 teaspoon sesame seeds - optional"
        ]
    },
    "Japchae": {
        "Main Ingredients": [
            "7 ounces Korean potato starch noodles (dangmyeon, 당면)",
            "1 carrot (about 3 ounces)",
            "1/2 medium onion (preferably sweet variety, 4 to 5 ounces)",
            "2 scallions",
            "4 ounces lean tender beef (sirloin, chuck tender, rib eye, etc.) or pork loin",
            "3 to 4 ounces fresh shiitake mushrooms (or 4 to 5 dried shiitake, soaked until plump)",
            "6 ounces fresh spinach (preferably a bunch of spinach)",
            "oil for stir frying",
            "salt",
            "egg garnish (jidan) - optional"
        ],
        "Sauce": [
            "3.5 tablespoons soy sauce",
            "3 tablespoons sugar (or brown sugar, you can use a little less if you want)",
            "2 tablespoons sesame oil",
            "2 teaspoons minced garlic",
            "1 tablespoon roasted sesame seeds",
            "black pepper to taste"
        ]
    },
    
}



ORDER_OUT_OPTIONS = [
    'Order out Korean', 'Order out Japanese', 'Order out Thai', 
    'Order out Chinese', 'Order out Mexican', 'Order out Italian', 
    'Order out Fast food'
]

DAYS_OF_WEEK = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

def generate_meal_plan():
    """Generate a weekly meal plan."""
    order_out_day = random.choice(DAYS_OF_WEEK)
    meal_plan = {
        day: random.choice(ORDER_OUT_OPTIONS) if day == order_out_day else random.choice(COOK_OPTIONS)
        for day in DAYS_OF_WEEK
    }
    return pd.DataFrame(meal_plan.values(), index=meal_plan.keys(), columns=['Meal']).T

def send_email(meal_df):
    """Send the meal plan via email."""
    sender_email = config.EMAIL_USERNAME
    password = config.EMAIL_PASSWORD

    if not sender_email or not password:
        raise ValueError("Email credentials not found. Ensure they are set in the .env file.")

    receiver_email = sender_email
    meal_html = meal_df.to_html(index=False, border=0)
    body = f"""
    <html>
        <body>
            <p>Here is your weekly meal plan:</p>
            {meal_html}
        </body>
    </html>
    """

    # Set up the MIME message
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body, 'html'))

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Send the email
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Email sent to {receiver_email}")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")
    
def main():
    """Main function to generate meal plan and send email."""
    meal_df = generate_meal_plan()
    print(meal_df)
    send_email(meal_df)

    # Convert DataFrame to markdown format
    markdown_content = meal_df.to_markdown(index=False)
    
    # Save the markdown to a file
    # with open('weekly_meal_plan_export.txt', 'w') as file:
    #     file.write(markdown_content)
    
    # print("Markdown file 'weekly_meal_plan.md' has been saved.")

if __name__ == "__main__":
    main()
