import streamlit as st
import os
import requests
from datetime import datetime,timedelta

os.environ["STREAMLIT_SERVER_PORT"] = os.environ.get("PORT", "8501")

st.markdown(
   """
    <div style="background-color:#d0f0c0; padding:10px; border-radius:10px; text-align:center">
        <h3 style="color:#333;">Welcome to <b>Tailor Talk</b> - Smart Appointment Scheduler 📅</h3>
    </div>
    """, unsafe_allow_html=True
)

st.set_page_config(page_title="Tailor Talk",layout="centered")

st.title("Tailor Talk-Appointment Scheduler")

option=st.sidebar.selectbox("Select Action",["📅 View Appointments","📝 Book Appointment","❌ Cancel Appointment","🔁 Reschedule an Appointment","⏳ Check Availability","🟢 View Free Slots","💬 Chat"])

if option.startswith("📅"):
    st.subheader("📅 Your Upcoming Appointments")

    try:
     with st.spinner("Fetching appointments..."):
        response=requests.get("http://127.0.0.1:8000/appointments")
        data=response.json()
        appointments=data.get("appointments",[])

        if appointments:
            for appt in appointments:
                st.write(f" **Title:** {appt['summary']}")
                st.write(f" **Start:** {appt['start_time']}")
                st.write(f" **End:** {appt['end_time']}")
                st.write(f" [Open Event]({appt['link']})")
                st.markdown("---")
        else:
            st.info("No upcoming appointments found.")
    except Exception as e:
        st.error(f"Failed to fetch appointments: {e}")


elif option.startswith("📝"):
    st.subheader("📝 Book a New Appointment")
    st.write("You can leave fields empty to auto-book the next available 30-minute slot.")

    title=st.text_input("Title",value="Tailor Booking")
    description=st.text_area("Description",value="Scheduled via chatbot")
     
    use_custom_time=st.checkbox("Use custom start and end time")

    if use_custom_time:
        col1,col2=st.columns(2)
        with col1:
            start_date=st.date_input("Start Date")
            start_time=st.time_input("Start Time")
        with col2:
            end_date=st.date_input("End Date")
            end_time=st.time_input("End Time")
        start_dt=datetime.combine(start_date,start_time)
        end_dt=datetime.combine(end_date,end_time)
    else:
        start_dt=datetime.utcnow() + timedelta(hours=1)
        end_dt=start_dt + timedelta(minutes=30)
    
    if st.button("Book Appointment"):
        payload={"title":title,"description":description,"start_time":start_dt.isoformat(),"end_time":end_dt.isoformat()}

        try:
          with st.spinner("Booking appointment..."):  
            response=requests.post("http://127.0.0.1:8000/book",json=payload)
            data=response.json()
            if "event_link" in data:
                st.success(f"Appointment booked! [Click to View]({data['event_link']})")
            else:
                st.error(f"Error:{data.get('error','Unknown error')}")
        except Exception as e:
            st.error(f"Failed to book appointment:{e}")

elif option.startswith("❌"):
    st.subheader("❌ Cancel an Appointment")

    try:
      with st.spinner("Loading appointments..."):  
        response=requests.get("http://127.0.0.1:8000/appointments")
        data=response.json()
        appointments=data.get("appointments",[])

        if appointments:
            appointment_titles=[f"{a['summary']} ({a['start_time']} to {a['end_time']})" for a in appointments]
            selected=st.selectbox("Select Appointment to Cancel", appointment_titles)
            event_id=appointments[appointment_titles.index(selected)]["event_id"]

            if st.button("Cancel Appointment"):
              with st.spinner("Cancelling..."):  
                cancel_response=requests.delete(f"http://127.0.0.1:8000/cancel/{event_id}")
                result=cancel_response.json()
                if "message" in result:
                    st.success(result["message"])
                else:
                    st.error(result.get("error","Unknown error occurred."))
        else:
            st.info("No appointments to cancel.")
    except Exception as e:
        st.error(f"Failed to fetch or cancel appointments: {e}")

elif option.startswith("🔁"):
    st.subheader("🔁 Reschedule an Appointment")

    try:
      with st.spinner("Fetching appointments..."):  
        response=requests.get("http://127.0.0.1:8000/appointments")
        data=response.json()
        appointments=data.get("appointments",[])

        if appointments:
            appointment_titles=[f"{a['summary']} ({a['start_time']} to {a['end_time']})" for a in appointments]
            selected=st.selectbox("Select Appointment to Reschedule",appointment_titles)
            event_id=appointments[appointment_titles.index(selected)]["event_id"]

            new_start=st.text_input("New Start Time (YYYY-MM-DDTHH:MM)", "")
            new_end=st.text_input("New End Time (YYYY-MM-DDTHH:MM)", "")

            if st.button("Reschedule Appointment"):
                if new_start and new_end:
                    payload={"event_id":event_id,"new_start":new_start,"new_end":new_end}

                    try:
                       with st.spinner("Rescheduling..."):  
                        res=requests.put("http://127.0.0.1:8000/reschedule",json=payload)
                        result=res.json()
                        if "event_link" in result:
                            st.success(f"Appointment rescheduled! [Click to View]({result['event_link']})")
                        else:
                            st.info(result.get("message","Rescheduled."))
                    except Exception as e:
                        st.error(f"Error during rescheduling:{e}")
                else:
                    st.warning("Please enter both new start and end times.")
        else:
            st.info("No appointments available for rescheduling.")
    except Exception as e:
        st.error(f"Failed to fetch appointments:{e}")


elif option.startswith("⏳"):
    st.subheader("⏳ Check Availability (Next 24 Hours)")
    try:
      with st.spinner("Checking..."):  
        response=requests.get("http://127.0.0.1:8000/availability")
        data=response.json()
        busy_slots=data.get("busy_slots",[])

        if busy_slots:
            for slot in busy_slots:
                st.write(f" **Busy From:** {slot['start']} — **To:** {slot['end']}")
        else:
            st.success("✅  No busy slots found! The calendar is fully free in the next 24 hours.")

    except Exception as e:
        st.error(f"Failed to fetch availability: {e}")

elif option.startswith("🟢"):
    st.subheader("🟢 Available Time Slots (Next 8 Hours)")

    try:
      with st.spinner("Loading..."):  
        response=requests.get("http://127.0.0.1:8000/free-slots")
        data=response.json()
        slots=data.get("free_slots",[])

        if slots:
            for slot in slots:
                st.write(f"**Start:** {slot['start']} → **End:** {slot['end']}")
                st.markdown("---")
        else:
            st.info("No free slots found in the next 8 hours.")
    except Exception as e:
        st.error(f"Failed to load free slots: {e}")

elif option.startswith("💬"):
    st.subheader("💬 Chat with Tailor Assistant")

    chat_history=st.empty()
    user_message=st.text_input("You:", "",key="chat_input")

    if st.button("Send"):
        if user_message.strip():
            try:
                with st.spinner("Sending message..."):
                    payload={"message": user_message}
                    response=requests.post("http://127.0.0.1:8000/chat", json=payload)
                    data=response.json()
                    bot_reply=data.get("response", "No response from bot.")

                st.markdown(f"<div style='background-color:#f0f0f5; padding:10px; border-radius:10px;'><b>You:</b> {user_message}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='background-color:#d1e7dd; padding:10px; border-radius:10px;'><b>Bot:</b> {bot_reply}</div>", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"Error talking to the bot:{e}")
        else:
            st.warning("Please enter a message before sending.")
