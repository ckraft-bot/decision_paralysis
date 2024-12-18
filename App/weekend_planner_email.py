# import config
from dotenv import dotenv_values
import os
import random
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Constants
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 465
SUBJECT = "Weekend Plan"

DAY_LIST = ['Friday', 'Saturday', 'Sunday']

EXERCISE_LIST = [
    'climb', 'hike', 'paddle board', 'rock climb', 'run', 'stretch', 'walk'
]

CHORE_LIST = [
    'do laundry', 'dust', 'garden', 'grocery shop', 'mop', 'mow the lawn', 
    'scoop the litter', 'trim cat nails', 'vacuum', 'wash car', 'water plants'
]

LEISURE_LIST = [
    'call a family', 'call a friend', 'code', 'journal', 'listen to music/podcast',
    'nap', 'play Xbox', 'practice a foreign language of choice', 'read a book',
    'speed cube', 'watch a movie', 'watch a tv show'
]


def generate_activity_plan():
    """
    Generates a weekly plan of activities (exercise, chore, leisure) for each day
    and returns the itinerary as a string.
    """
    itinerary = ""
    
    # Loop through the days (Friday, Saturday, Sunday)
    for day in DAY_LIST:
        itinerary += f"{day}:\n"
        
        # Select one exercise, two chores, and two leisure activities
        selected_activities = [random.choice(EXERCISE_LIST)]
        selected_activities += random.sample(CHORE_LIST, k=2)
        selected_activities += random.sample(LEISURE_LIST, k=2)

        # Format the activities for the current day
        for activity in selected_activities:
            itinerary += f"- {activity}\n"
        itinerary += '\n'

    return itinerary


def compose_email_body(itinerary):
    """
    Composes the email body with the provided itinerary.
    """
    return f"""
    <html>
        <body>
            <p>Here is your weekend plan:</p>
            <pre>{itinerary}</pre>
        </body>
    </html>
    """


def send_email(itinerary):
    """
    Sends the composed email with the itinerary to the user.
    """
    secrets = dotenv_values(".env")
    sender_email = secrets["EMAIL_USERNAME"]
    password = secrets["EMAIL_PASSWORD"]

    if not sender_email or not password:
        raise ValueError("Email credentials not found. Ensure they are set in the .env file.")
    
    receiver_email = sender_email
    body = compose_email_body(itinerary)

    # Compose the email message
    msg = MIMEMultipart('alternative')
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = SUBJECT
    msg.attach(MIMEText(body, 'html'))

    # Send the email
    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=ssl.create_default_context()) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print(f"Email sent to {receiver_email}")
    except smtplib.SMTPException as e:
        print(f"Failed to send email: {e}")

def main():
    """
    Main function to generate the activity plan and send the email.
    """
    itinerary = generate_activity_plan()
    print(itinerary)
    send_email(itinerary)

if __name__ == '__main__':
    main()
