import config
import os
import random
import pywhatkit

# Constants
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


def send_message(itinerary):
    """
    Sends the composed WhatsApp message with the itinerary to the user.
    """
    phone = config.PHONE_NUMBER  # Assumes the phone number is set in the config file
    message = itinerary
    pywhatkit.sendwhatmsg_instantly(phone, message, 10)  # Sends the message with a 10-second delay


def main():
    """
    Main function to generate the activity plan and send the message.
    """
    itinerary = generate_activity_plan()
    print(itinerary)  # Print the itinerary for verification
    send_message(itinerary)  # Send the itinerary message


if __name__ == '__main__':
    main()
