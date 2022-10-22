import os
import datetime
from google.auth.transport import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def get_credentials():
    """
    function to get correct credentials or use already existing ones
    :return: credentials
    """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if creds is None or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    return creds


def get_available_calendars(service):
    calendars = service.calendarList().list().execute()
    return calendars['items']


def get_events_from_calendar(service, calendar_id='primary'):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    end_of_today = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    end_of_today = end_of_today.isoformat() + 'Z'
    return service.events().list(calendarId=calendar_id, timeMin=now, timeMax=end_of_today).execute().get('items', [])


def main():
    try:
        service = build('calendar', 'v3', credentials=get_credentials())
        calendars = get_available_calendars(service)
        for elem in calendars:
            print('fetching data for: ', elem['id'])
            events = get_events_from_calendar(service, elem['id'])
            if len(events) == 0:
                print('no upcoming events')
            for event in events:
                print(event['summary'], ' at ', event['start'], '\n', event['htmlLink'])
    except Exception as e:
        print('smth went wrong')
        print(e)


if __name__ == '__main__':
    main()
