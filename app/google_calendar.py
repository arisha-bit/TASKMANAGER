from googleapiclient.discovery import build

def add_event_to_calendar(task_title, task_date, creds):
    service = build('calendar', 'v3', credentials=creds)
    event = {
        'summary': task_title,
        'start': {'dateTime': task_date + "T09:00:00", 'timeZone': 'Asia/Kolkata'},
        'end': {'dateTime': task_date + "T10:00:00", 'timeZone': 'Asia/Kolkata'}
    }
    service.events().insert(calendarId='primary', body=event).execute()
