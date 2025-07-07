# Tailor Talk 🤖📅 – Smart Appointment Scheduler

Tailor Talk is a conversational AI agent that lets users schedule appointments on Google Calendar using a chatbot interface. Built using **FastAPI**, **Langchain**, and **Streamlit**, it offers a natural way to interact with your calendar without clicking through complex UI.

---

## 🔥 Features

✅ Conversational AI agent  
✅ Book, cancel, and reschedule appointments  
✅ Google Calendar integration (via Service Account)  
✅ Detects free/busy slots automatically  
✅ Streamlit UI for chatbot and calendar operations  
✅ Real-time booking and feedback  
✅ Built-in event reminder (30 minutes before the meeting)  
✅ Simple UI with no login required

---

## 🛠️ Tech Stack

| Component     | Technology                           |
|---------------|--------------------------------------|
| Backend       | FastAPI                              |
| Agent         | Langchain + GPT (via OpenRouter)     |
| Calendar API  | Google Calendar (Service Account)    |
| Frontend      | Streamlit                            |
| Deployment    | Render                               |

---

## 🚀 How It Works

1. User types a natural message like “Book a meeting tomorrow at 3PM”
2. Langchain agent understands the intent using GPT
3. Backend handles the logic: booking, checking slots, canceling, etc.
4. Google Calendar is updated via API (with a popup reminder 30 minutes before the event)
5. Streamlit shows updates instantly with links to events

---

## 💬 Agent Prompt Examples

- `Hi 👋`  
- `Book an appointment`  
- `Are you free tomorrow?`  
- `Cancel appointment with id xyz123`  
- `Reschedule my meeting`

---

## 📦 Folder Structure

Tailor-Talk-bot/
│
├── backend/
│ ├── main.py
│ ├── agent.py
│ ├── calendar_service.py
│ ├── requirements.txt
│ └── .env (not committed)
│
├── frontend/
│ ├── streamlit_app.py
│ └── requirements.txt
│
├── .gitignore
├── service_account.json (not committed)
├── README.md


---

## ⚙️ Setup Instructions

### 🔹 Backend (FastAPI + Langchain)

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload


🔹 Frontend (Streamlit)
bash
Copy
Edit
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py


🔐 Environment Setup
Create a .env file in the /backend directory:

ini
Copy
Edit
OPENROUTER_API_KEY=your_openrouter_api_key
CALENDAR_ID=your_google_calendar_id
Also, ensure service_account.json is placed securely in the backend folder and excluded in .gitignore.


🌐 Live Project Links

🔗 Frontend (Streamlit UI): https://tailor-talk-bot-frontend.onrender.com

🔗 Backend (FastAPI): https://tailor-talk-bot-9v6q.onrender.com

📦 GitHub Repo: https://github.com/Charan152315/tailor-talk-bot.git

🧠 Agent Integration (Langchain)
Uses initialize_agent() with multi-function tools to manage:

check availability

book appointment

respond to greetings, questions, etc.

Powered by GPT-4o via OpenRouter API

👨‍💻 Developed By
Charan Sri
Backend Developer | AI Builder | NIT Raipur

📌 Notes

🔒 No OAuth used — secured via Google Service Account

📅 App books 30-minute slots by default

⏰ Popup event reminder 30 minutes before meeting

🌍 Fully deployable on Render 

📤 Submission Checklist ✅

✅ Hosted Streamlit URL
✅ GitHub Repo with full code
✅ Working backend agent via FastAPI
✅ Google Calendar integration
✅ Booking + Chat functionality
✅ Reminder popup configured


---