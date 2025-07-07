from fastapi import FastAPI
from datetime import datetime,timedelta,timezone
from calendar_service import check_free_slots, book_appointment,get_all_appointments,cancel_appointment,reschedule_appointment
import csv
import os
from agent import run_agent
from pydantic import BaseModel

app=FastAPI()

@app.get("/")
def root():
    return {"message":"Tailor Talk API is running!"}

@app.get("/availability")
def check_availability():
    now=datetime.utcnow()
    one_day_availability=now+timedelta(days=1)
    busy=check_free_slots(now,one_day_availability)
    return {"busy_slots":busy}

@app.get("/free-slots")
def get_free_slots():
    now=datetime.now(timezone.utc)
    end_of_day=now + timedelta(hours=8) 

    busy_slots=check_free_slots(now,end_of_day)

    free_slots=[]
    current=now

    for slot in busy_slots:
        busy_start=datetime.fromisoformat(slot["start"])
        busy_end=datetime.fromisoformat(slot["end"])

        if current < busy_start:
            free_slots.append({"start": current.isoformat(),"end": busy_start.isoformat()})
        current=max(current,busy_end)

    if current < end_of_day:
        free_slots.append({"start":current.isoformat(),"end":end_of_day.isoformat()})

    return {"free_slots":free_slots}


class BookingRequest(BaseModel):
    title:str
    description:str
    start_time:str 
    end_time:str

@app.post("/book")
def book_custom_slot(data:BookingRequest):
    start=datetime.fromisoformat(data.start_time)
    end=datetime.fromisoformat(data.end_time)
    busy = check_free_slots(start,end)
    if busy:
        return {"error":"Selected time slot is not available."}
    link=book_appointment(data.title,data.description,start,end)
    return {"event_link":link}

@app.post("/book_default")
def book_default():
   
   now=datetime.utcnow() + timedelta(hours=1)
   end_of_day=now.replace(hour=18,minute=0,second=0,microsecond=0)

   slot_duration=timedelta(minutes=30)
   current_start=now

   while current_start + slot_duration <= end_of_day:
        current_end = current_start + slot_duration
        busy = check_free_slots(current_start,current_end)
        if not busy:
            link=book_appointment("Tailor Booking","Scheduled via default",current_start,current_end)
            return {"event_link": link}
        current_start += timedelta(minutes=30)

   return{"error":"No available 30-minute slot found for today."}


class ChatRequest(BaseModel):
    message:str

@app.post("/chat")
def chat_with_model(chat:ChatRequest):
    msg=chat.message.lower().strip()

    greetings=["hi","hello","hey","yo"]
    farewells=["bye","goodbye","see you","take care"]
    thanks=["thank you","thanks","thx"]
    how_are_you=["how are you","how's it going","how are you doing"]

    if any(word in msg for word in greetings):
        return {"response": "Hello! 👋 How can I help you book an appointment today?"}

    elif any(word in msg for word in farewells):
        return {"response": "Goodbye! 👋 Let me know if you need anything else."}

    elif any(word in msg for word in thanks):
        return {"response": "You're welcome! 😊 Happy to help."}

    elif any(q in msg for q in how_are_you):
        return {"response": "I'm just a bot, but I'm here and ready to help! 🤖  How can I assist you?"}
    
    try:
        response=run_agent(chat.message)
        return {"response":response["output"]}
    except Exception as e:
        return {"response": f"Sorry, I had an error: {e}"}

@app.get("/appointments")
def view_appointments():
    appointments=get_all_appointments()
    return {"appointments":appointments}

@app.delete("/cancel/{event_id}")
def cancel(event_id:str):
    result=cancel_appointment(event_id)
    return result

class RescheduleRequest(BaseModel):
    event_id:str
    new_start:str 
    new_end:str

@app.put("/reschedule")
def reschedule(data:RescheduleRequest):
    start=datetime.fromisoformat(data.new_start)
    end=datetime.fromisoformat(data.new_end)
    return reschedule_appointment(data.event_id,start,end)    