from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.tools import tool
import os
from dotenv import load_dotenv
from langchain.agents import initialize_agent,Tool
from calendar_service import check_free_slots,book_appointment as create_calendar_event
from datetime import datetime,timedelta

load_dotenv()

def check_availability(input=None) -> str:
    """Check if the calendar is busy in the next 24 hours."""
    now=datetime.utcnow()
    one_day_availability=now + timedelta(days=1)
    busy=check_free_slots(now,one_day_availability)
    return f"Busy slots:{busy}" if busy else "You are free for the next 24 hours."

def book_appointment(input=None) -> str:
    """Book a default 30-minute appointment starting 1 hour from now."""
    now=datetime.utcnow() + timedelta(hours=1)
    end=now + timedelta(minutes=30)
    link=create_calendar_event("Tailor Booking","Scheduled via chatbot",now,end)
    return f"Your appointment has been booked successfully! Here's your event link:{link}"

llm=ChatOpenAI(model="openai/gpt-4o",openai_api_key=os.getenv("OPENROUTER_API_KEY"),openai_api_base="https://openrouter.ai/api/v1", max_tokens=1000,)

tools=[
    Tool.from_function(
        func=check_availability,
        name="check_availability",
        description="Check if the calendar is busy in the next 24 hours"
    ),
    Tool.from_function(
        func=book_appointment,
        name="book_appointment_tool",
        description="Book a default 30-minute appointment"
    )
]

agent=initialize_agent(tools=tools,llm=llm,agent_type=AgentType.OPENAI_MULTI_FUNCTIONS,verbose=True)

def run_agent(message:str):
    response=agent.invoke({"input":message})
    return response
