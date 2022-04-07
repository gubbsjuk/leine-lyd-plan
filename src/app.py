import json

import streamlit as st

from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.

st.title("Leine lyd liker å planlegge spillelister!")
st.text("(men gjør dette mest fordi mange bartendere er ubrukelige...)")

with open("src/plan.json", "r") as file:
    plans = json.load(file)

st.subheader("Add to plan")
with st.form(key="playlist_entry_form"):
    playlist = st.selectbox("Playlist", ("Clown Core", "Not Clown Core"))
    start_day = st.selectbox(
        "Day",
        ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
    )
    start_time = st.time_input("Start time")
    duration = st.number_input("Duration (hours)", min_value=0, max_value=24, value=8)
    if st.form_submit_button("Submit"):
        plans.append(
            {
                "playlist": playlist,
                "start_day": start_day,
                "start_time": start_time.isoformat(),
                "duration": duration,
            }
        )

with open("src/plan.json", "w") as outfile:
    json.dump(plans, outfile)

st.subheader("Your plan")

for i, plan in enumerate(plans):
    with st.form(f"playlist_remove_{i}"):
        st.write(plan["playlist"], key=f"playlist_{i}")
        st.write(
            "Start on", plan["start_day"], plan["start_time"], key=f"start_day_{i}"
        )
        st.write("Play for", plan["duration"], "hours", key=f"duration_{i}")
        if st.form_submit_button("Delete"):
            plans.pop(i)

with open("src/plan.json", "w") as outfile:
    json.dump(plans, outfile)

# st.balloons()
