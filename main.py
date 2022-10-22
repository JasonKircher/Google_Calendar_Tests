import os
import datetime
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


def get_events_from_today(service, calendar_id='primary'):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    end_of_today = datetime.datetime.utcnow() + datetime.timedelta(days=1)
    end_of_today = end_of_today.isoformat() + 'Z'
    return service.events().list(calendarId=calendar_id, timeMin=now, timeMax=end_of_today).execute().get('items', [])


def get_next_event_specific(service, calendar_id='primary'):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    return service.events().list(calendarId=calendar_id, timeMin=now, maxResults=1, orderBy='startTime', singleEvents=True).execute().get('items', [])[0]


def get_events_today(service):
    calendars = get_available_calendars(service)
    out = []
    for elem in calendars:
        events = get_events_from_today(service, elem['id'])
        if len(events) == 0:
            print('no upcoming events')
        for event in events:
            print(event['summary'], ' at ', event['start'], '\n', event['htmlLink'])
            out.append(event)
    return out


def get_next_event(service):
    events = []
    for elem in get_available_calendars(service):
        events.append({'calendar': elem["id"], 'event': get_next_event_specific(service, elem["id"])})

    for elem in events:
        if 'group.v.calendar.google.com' in elem['calendar']:
            continue
        try:
            start = elem['event']['start']['dateTime']
            start = datetime.datetime.strptime(start, '%Y-%m-%dT%H:%M:%S%z')
            now = datetime.datetime.now().astimezone(start.tzinfo)
        except:
            start = elem['event']['start']['date']
            start = datetime.datetime.strptime(start, '%Y-%m-%d').date()
            now = datetime.date.today()

        time_delta = start - now
        seconds = time_delta.seconds % 60
        minutes = time_delta.seconds // 60 % 60
        hours = time_delta.seconds // 60 // 60

        calendar = elem['calendar'] if 'sv4ongbp9nh3g2h1o4r529o5h2hetehq' not in elem['calendar'] else 'KIT'

        prefix = 'next event in ' + str(time_delta.days) + ' days, ' + str(hours) + ' hours, ' + str(minutes) + ' minutes, ' + str(seconds) + ' seconds' if not time_delta.days == seconds == minutes == hours == 0 else 'ongoing event '
        print(calendar + '\n' + prefix)
        print(elem['event']['summary'])

def main():
    try:
        service = build('calendar', 'v3', credentials=get_credentials())
        #print('looking for events today...')
        #get_events_today(service)
        print('looking for next event...')
        get_next_event(service)
    except Exception as e:
        print('smth went wrong')
        print(e)


if __name__ == '__main__':
    main()
