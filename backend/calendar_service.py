from googleapiclient.discovery import build
import os
import csv
import uuid
from dotenv import load_dotenv
from datetime import timezone
from google.oauth2 import service_account

load_dotenv()

SCOPES=["https://www.googleapis.com/auth/calendar"]
SERVICE_ACCOUNT_FILE="service_account.json"
CALENDAR_ID=os.getenv("CALENDAR_ID")

credentials=service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE,scopes=SCOPES)
service=build("calendar",'v3',credentials=credentials)

def check_free_slots(start_time,end_time):
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)

    body = {"timeMin":start_time.isoformat(),"timeMax":end_time.isoformat(),"timeZone":"UTC","items":[{"id":CALENDAR_ID}]}

    check_result=service.freebusy().query(body=body).execute()
    busy_schedule=check_result["calendars"][CALENDAR_ID]["busy"]
    return busy_schedule

def book_appointment(title,description,start_time,end_time):
    event={"summary":title,"description": description,
        "start":{'dateTime':start_time.isoformat(),'timeZone':'UTC',},
        "end":{'dateTime':end_time.isoformat(),'timeZone': 'UTC',},
        "reminders":{"useDefault":False,"overrides":[{"method":"popup","minutes":30}]},}
    
    created_event = service.events().insert(calendarId=CALENDAR_ID,body=event).execute()

    file_exists = os.path.exists("appointments.csv")
    with open("appointments.csv","a",newline='') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["event_id","summary","start_time","end_time","link"])
        writer.writerow([created_event.get("id"),title,start_time.isoformat(),end_time.isoformat(),created_event.get("htmlLink")])

    return created_event.get("htmlLink")

def get_all_appointments():
     appointments=[]

     if not os.path.exists("appointments.csv"):
          return appointments
     
     with open("appointments.csv","r") as f:
        reader=csv.DictReader(f)
        for row in reader:
            appointments.append({"event_id": row["event_id"],"summary": row["summary"],"start_time": row["start_time"],"end_time": row["end_time"],"link": row["link"]})
     return appointments 

def cancel_appointment(event_id):
    try:
        service.events().delete(calendarId=CALENDAR_ID, eventId=event_id).execute()
    except Exception as e:
        return {"error":f"Failed to delete from calendar:{e}"}

    updated_rows=[]
    if os.path.exists("appointments.csv"):
        with open("appointments.csv","r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row["event_id"]!=event_id:
                    updated_rows.append(row)

        with open("appointments.csv","w",newline="") as f:
            writer=csv.DictWriter(f,fieldnames=["event_id","summary","start_time","end_time","link"])
            writer.writeheader()
            writer.writerows(updated_rows)

    return {"message":"Appointment cancelled successfully"}

def reschedule_appointment(event_id,new_start_time,new_end_time):
    updated_rows=[]
    old_row=None

    if not os.path.exists("appointments.csv"):
        return {"error":"No appointments to update"}
    
    with open("appointments.csv","r") as f:
        reader=csv.DictReader(f)
        for row in reader:
            if row["event_id"]==event_id:
                old_row=row
            else:
                updated_rows.append(row)

    if not old_row:
        return {"error":"Appointment not found"}
    
    try:
        service.events().delete(calendarId=CALENDAR_ID,eventId=event_id).execute()
    except Exception as e:
        return {"error":f"Failed to delete old event:{e}"}
    
    new_event={"summary":old_row["summary"],"description":"Rescheduled via API","start": {"dateTime":new_start_time.isoformat(),"timeZone":"UTC"},"end": {"dateTime":new_end_time.isoformat(),"timeZone":"UTC"}}

    created_event=service.events().insert(calendarId=CALENDAR_ID,body=new_event).execute()

    with open("appointments.csv","w",newline="") as f:
        writer=csv.DictWriter(f,fieldnames=["event_id","summary","start_time","end_time","link"])
        writer.writeheader()
        writer.writerows(updated_rows)
        writer.writerow({"event_id":created_event["id"],"summary":old_row["summary"],"start_time":new_start_time.isoformat(),"end_time":new_end_time.isoformat(),"link":created_event.get("htmlLink")})

    return {"message":"Rescheduled successfully","event_link":created_event.get("htmlLink")}



