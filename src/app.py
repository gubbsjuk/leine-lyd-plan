import sqlite3

import spotipy
import streamlit as st

from dotenv import load_dotenv
from spotipy.cache_handler import MemoryCacheHandler
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from constants import SCOPES
from models.db import Device, Schedule
from spotipy_utils import SQLiteCacheHandler


engine = create_engine(
    "sqlite:///5l.db", echo=False, future=True
)  # TODO: Check if this can be run only once..

load_dotenv()  # take environment variables from .env.


def get_token(oauth, code):
    token = oauth.get_access_token(code, as_dict=False, check_cache=True)
    return token


def app_get_token():
    try:
        token = get_token(st.session_state["oauth"], st.session_state["code"])
    except Exception as e:
        st.error("An error occurred during token retrieval!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["cached_token"] = token


def app_sign_in():
    try:
        sp = spotipy.Spotify(auth=st.session_state["cached_token"])
    except Exception as e:
        st.error("An error occurred during sign-in!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["signed_in"] = True
        st.session_state["spotify_user_uri"] = sp.current_user()["uri"]

        # Retrive oauth with MemoryCacheHandler from streamlit cache, and get cached token.
        oauth = st.session_state["oauth"]
        token = oauth.cache_handler.get_cached_token()
        # Create SQL Cache handler and populate with token from the MemoryCacheHandler.
        sql_cache = SQLiteCacheHandler(
            username=st.session_state["spotify_user_uri"], db_path="5l.db"
        )
        sql_cache.save_token_to_cache(token)
        oauth.cache_handler = sql_cache

        show_login_page()

    return sp


def app_sidebar(spotify, engine):
    # Setup session variables
    if "device_map" not in st.session_state:
        devices = (
            spotify.devices()
        )  # TODO: Update devices at some interval.. (Now just first time). Maybe "refresh" button?
        st.session_state.device_map = {d["name"]: d["id"] for d in devices["devices"]}

    st.sidebar.title("Configuration")
    with st.sidebar.form(key="device_entry_form"):
        device_name = st.selectbox("Device:", st.session_state.device_map.keys())

        if st.form_submit_button("Submit"):
            device_entry = {
                "user_uri": spotify.current_user()["uri"],
                "device_id": st.session_state.device_map[device_name],
                "device_name": device_name,
            }

            with Session(engine) as session:
                session.merge(Device(**device_entry))
                session.commit()


def show_login_page():
    oauth = st.session_state["oauth"]
    # retrieve auth url
    auth_url = oauth.get_authorize_url()
    link_html = f' <a target="_self" href="{auth_url}" >Click me to authenticate!</a> '
    welcome_msg = """
    Welcome! :wave: This app uses the Spotify API to interact with general
    music info and your playlists! In order to view and modify information
    associated with your account, you must log in. You only need to do this
    once.
    """
    st.title("Leine Lyds lille lyd-løsning.")

    if not st.session_state["signed_in"]:
        st.markdown(welcome_msg)
        st.write(" ".join(["Please log in by clicking the link below."]))
        st.markdown(link_html, unsafe_allow_html=True)


def show_main_page(spotify, engine):
    app_sidebar(spotify, engine)

    if "playlist_map" not in st.session_state:
        playlists = spotify.current_user_playlists(limit=50)
        # TODO: Maybe refresh button here too?
        st.session_state.playlist_map = {
            p["name"]: p["uri"] for p in playlists["items"]
        }

    with Session(engine) as session:  # TODO: This query is probably redundant.
        dev = session.query(Device.device_name).first()
        session.commit()  # TODO: Is this needed?

        if dev:
            st.text("Playback on device: " + dev[0])
        else:
            st.text("Please select playback device.")

    st.subheader("Add to plan", anchor="add")
    with st.form(key="playlist_entry_form"):
        playlist = st.selectbox("Playlist", st.session_state.playlist_map.keys())
        start_day = st.selectbox(
            "Day",
            (
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ),
        )
        start_time = st.time_input("Start time")
        if st.form_submit_button("Submit"):
            plan_entry = {
                "user_uri": st.session_state["spotify_user_uri"],
                "playlist": playlist,
                "playlist_uri": st.session_state.playlist_map[playlist],
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
        plans = session.query(Schedule).where(
            Schedule.user_uri == st.session_state["spotify_user_uri"]
        )

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
                        playlist_uri=plan.playlist_uri,
                        start_day=plan.start_day,
                        start_time=plan.start_time,
                    ).delete()
                    session.commit()
                raise st.experimental_rerun()


# Application

if "signed_in" not in st.session_state:
    st.session_state["signed_in"] = False
if "cached_token" not in st.session_state:
    st.session_state["cached_token"] = ""
if "code" not in st.session_state:
    st.session_state["code"] = ""
if "oauth" not in st.session_state:
    oauth = SpotifyOAuth(
        scope=SCOPES,
        cache_handler=MemoryCacheHandler(),
    )
    st.session_state["oauth"] = oauth

url_params = st.experimental_get_query_params()

# attempt sign in with cached token
if st.session_state["cached_token"] != "":
    sp = app_sign_in()
# if no token, but code in url, get code, parse token, and sign in
elif "code" in url_params:
    # all params stored as lists, see doc for explanation
    st.session_state["code"] = url_params["code"][0]
    st.experimental_set_query_params()  # remove code from url params
    app_get_token()
    sp = app_sign_in()
else:
    show_login_page()

# only display the following after login
if st.session_state["signed_in"]:
    # TODO: Exchange Streamlit cache with SQLCache

    show_main_page(sp, engine)

    con = sqlite3.connect("5l.db")
    cur = con.cursor()
    test = cur.execute("SELECT * FROM schedule").fetchall()
    con.close()

    st.write(test)
