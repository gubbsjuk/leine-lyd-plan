import spotipy
import streamlit as st

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from constants import CONFIG_PATH, PLAN_PATH
from utils import load_json, write_json


load_dotenv()  # take environment variables from .env.

# Load existing files they exist, else start a blank one..
plans = load_json(PLAN_PATH, {"updated": True, "plans": []})
config = load_json(CONFIG_PATH)

# scope = ["user-read-private", "user-read-email", "playlist-read-private", "playlist-read-public", "user-modify-playback-state"]
spotify = spotipy.Spotify(
    client_credentials_manager=SpotifyOAuth(
        scope=[
            "user-read-playback-state",
            "playlist-read-private",
            "user-modify-playback-state",
        ]
    )
)  # scope=scope))

if "device_map" not in st.session_state:
    devices = (
        spotify.devices()
    )  # TODO: Update devices at some interval.. (Now just first time).
    st.session_state.device_map = {d["name"]: d["id"] for d in devices["devices"]}

if "playlist_map" not in st.session_state:
    playlists = spotify.current_user_playlists(limit=50)
    st.session_state.playlist_map = {p["name"]: p["id"] for p in playlists["items"]}


st.sidebar.title("Configuration")
st.sidebar.selectbox("Account (NOT IMPLEMENTED YET)", ["Acc0", "Acc1"])

device_name = st.sidebar.selectbox("Device:", st.session_state.device_map.keys())
config["device_id"] = st.session_state.device_map.get(device_name, None)
write_json(CONFIG_PATH, config)

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
        plan = {
            "playlist": playlist,
            "playlist_id": st.session_state.playlist_map[playlist],
            "start_day": start_day,
            "start_time": start_time.isoformat(),
        }
        # TODO: Check if plan already exists..
        # if True:
        #    st.error("There is already an entry at this time. Please remove it first.")

        plans["plans"].append(plan)
        plans["updated"] = True
        write_json(PLAN_PATH, plans)
        st.balloons()  # TODO: Remove this shit :cry:


st.subheader("Your plan", anchor="plan")

for i, plan in enumerate(plans["plans"]):
    with st.form(f"playlist_remove_{i}"):
        st.write(plan["playlist"], key=f"playlist_{i}")
        st.write(
            "Start on", plan["start_day"], plan["start_time"], key=f"start_day_{i}"
        )
        if st.form_submit_button("Delete"):
            st.write("deleting", i)
            plans["plans"].pop(i)
            plans["updated"] = True
            write_json(PLAN_PATH, plans)
            raise st.experimental_rerun()
