import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.auth.transport.requests import Request

# If modifying or running for the first time, use the credentials.json you downloaded
CLIENT_SECRET_FILE = r'credentials.json'
API_NAME = 'calendar'
API_VERSION = 'v3'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# Authenticate and create the API client
# Step 2: Update the flow with a redirect URI
def authenticate():
    creds = None
    # Token file stores the user's access and refresh tokens, it is created automatically when the
    # authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            
            # Step 2: Explicitly set the redirect URI for local server
            flow.redirect_uri = 'http://localhost:8081'  # Updated port
            creds = flow.run_local_server(port=8081)  # Ensure the same port number is used

        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    # Build the API client
    service = googleapiclient.discovery.build(API_NAME, API_VERSION, credentials=creds)
    return service

# Example to list upcoming events
def list_events():
    service = authenticate()

    # Call the Calendar API
    events_result = service.events().list(calendarId='primary', timeMin='2025-02-01T00:00:00Z', maxResults=10, singleEvents=True, orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(f'{start}: {event["summary"]}')

if __name__ == '__main__':
    list_events()
