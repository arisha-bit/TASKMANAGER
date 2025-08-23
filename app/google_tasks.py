from googleapiclient.discovery import build

def add_task_to_google_tasks(task_title, task_date, creds):
    service = build('tasks', 'v1', credentials=creds)
    task = {'title': task_title, 'due': task_date + "T09:00:00.000Z"}
    service.tasks().insert(tasklist='@default', body=task).execute()
