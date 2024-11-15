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
    'Fruit smoothie', 'Gyeran', 'Japchae', 'Kimchi fried rice',
    'Kimbap bowl', 'Mandoo', 'Omurice', 'Pajun', 
    'Pad woon sen', 'Ramen', 'Tilapia & baked vegetables', 
    'Tofu jorim', 'rice & seaweed', 'Tomato and egg'
]

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
    # send_email(meal_df)

    # Convert DataFrame to markdown format
    markdown_content = meal_df.to_markdown(index=False)
    
    # Save the markdown to a file
    with open('weekly_meal_plan_export.txt', 'w') as file:
        file.write(markdown_content)
    
    print("Markdown file 'weekly_meal_plan.md' has been saved.")

if __name__ == "__main__":
    main()
