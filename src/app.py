import spotipy
import streamlit as st

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from models.device import Device
from models.schedule import Schedule


engine = create_engine(
    "sqlite:///5l.db", echo=False, future=True
)  # TODO: Check if this can be run only once..


load_dotenv()  # take environment variables from .env.

spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyOAuth(
        scope=[
            "user-read-playback-state",
            "playlist-read-private",
            "user-modify-playback-state",
        ]
    )
)

if "device_map" not in st.session_state:
    devices = (
        spotify.devices()
    )  # TODO: Update devices at some interval.. (Now just first time). Maybe "refresh" button?
    st.session_state.device_map = {d["name"]: d["id"] for d in devices["devices"]}

if "playlist_map" not in st.session_state:
    playlists = spotify.current_user_playlists(limit=50)
    # TODO: Maybe refresh button here too?
    st.session_state.playlist_map = {p["name"]: p["uri"] for p in playlists["items"]}


st.sidebar.title("Configuration")
st.sidebar.selectbox("Account (NOT IMPLEMENTED YET)", ["Acc0", "Acc1"])

# TODO: Add a db table for config stuff? Currently device is not passed from app to scheduler.
device_name = st.sidebar.selectbox("Device:", st.session_state.device_map.keys())
device_entry = {
    "user_id": spotify.current_user(),
    "device_id": device_name,
}

with Session(engine) as session:
    session.on_duplicate_key_update(Device(**device_entry))

st.title("Leine Lyds lille lyd-løsning.")
st.text(
    "Leine lyd liker å planlegge spillelister (men gjør dette mest fordi servitører er ubrukelige...)"
)

st.subheader("Add to plan", anchor="add")
with st.form(key="playlist_entry_form"):
    playlist = st.selectbox("Playlist", st.session_state.playlist_map.keys())
    start_day = st.selectbox(
        "Day",
        ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"),
    )
    start_time = st.time_input("Start time")
    if st.form_submit_button("Submit"):
        plan_entry = {
            "playlist": playlist,
            "playlist_id": st.session_state.playlist_map[playlist],
            "start_day": start_day.lower(),
            "start_time": start_time.isoformat(),
        }

        with Session(engine) as session:
            session.add(Schedule(**plan_entry))
            try:
                session.commit()
                st.balloons()  # TODO: Remove this shit :cry:
            except IntegrityError:
                st.error(
                    "There is already an entry at this time. Please remove it first."
                )


st.subheader("Your plan", anchor="plan")

with Session(engine) as session:
    plans = session.query(Schedule).all()

for i, plan in enumerate(plans):
    with st.form(f"playlist_remove_{i}"):
        st.write(plan.playlist, key=f"playlist_{i}")
        st.write(
            "Start on",
            plan.start_day.capitalize(),
            "at",
            plan.start_time,
            key=f"start_day_{i}",
        )
        if st.form_submit_button("Delete"):
            st.write("deleting", i)
            with Session(engine) as session:
                session.query(Schedule).filter_by(
                    playlist_id=plan.playlist_id,
                    start_day=plan.start_day,
                    start_time=plan.start_time,
                ).delete()
                session.commit()
            raise st.experimental_rerun()
