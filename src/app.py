# import spotipy
import streamlit as st

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

import auth

from models.db import Device, Schedule


def initialize_session_variables(st):
    if "signed_in" not in st.session_state:
        st.session_state["signed_in"] = False
    if "cached_token" not in st.session_state:
        st.session_state["cached_token"] = ""
    if "code" not in st.session_state:
        st.session_state["code"] = ""
    if "oauth" not in st.session_state:
        st.session_state["oauth"] = None

    # TODO: Move initalization of device_map and playlist_map here?
    # FIXME: Is this really neccearry?


def sign_in(st, url_params):
    # attempt sign-in with cached token.
    if st.session_state["cached_token"] != "":
        sp = auth.app_sign_in(st, welcome_page)  # TODO: insert success func.
        return sp
    # if no token, but code in url, get code, parse token and sign in.
    elif "code" in url_params:
        st.session_state["code"] = url_params["code"][0]
        auth.app_get_token(st)
        sp = auth.app_sign_in(st, welcome_page)  # TODO: insert success func.
        return sp
    # otherwise prompt for redirect.
    else:
        welcome_page()


def welcome_page(st):
    scope = [
        "user-read-playback-state",
        "playlist-read-private",
    ]

    oauth = SpotifyOAuth(scope=scope)
    st.session_state["oauth"] = oauth

    auth_url = oauth.get_authorize_url()

    # this SHOULD open the link in the same tab when Streamlit Cloud is updated
    # via the "_self" target
    link_html = ' <a target="_self" href="{url}" >{msg}</a> '.format(
        url=auth_url, msg="Click me to authenticate!"
    )

    st.title("Leine Lyds lille lyd-løsning.")
    st.text(
        "Leine lyd liker å planlegge spillelister (men gjør dette mest fordi servitører er ubrukelige...)"
    )

    if not st.session_state["signed in"]:
        st.text(
            "No tokens found for this session. Please log in by clicking the link below."
        )
        st.markdown(link_html, unsafe_allow_html=True)


def authenticated(spotify):
    if "device_map" not in st.session_state:
        devices = (
            spotify.devices()
        )  # TODO: Update devices at some interval.. (Now just first time). Maybe "refresh" button?
        st.session_state.device_map = {d["name"]: d["id"] for d in devices["devices"]}

    if "playlist_map" not in st.session_state:
        playlists = spotify.current_user_playlists(limit=50)
        # TODO: Maybe refresh button here too?
        st.session_state.playlist_map = {
            p["name"]: p["uri"] for p in playlists["items"]
        }

    st.sidebar.title("Configuration")

    with st.sidebar.form(key="device_entry_form"):
        device_name = st.selectbox("Device:", st.session_state.device_map.keys())

        if st.form_submit_button("Submit"):
            device_entry = {
                "user_id": spotify.current_user()["id"],
                "device_id": st.session_state.device_map[device_name],
                "device_name": device_name,
            }

            with Session(engine) as session:
                session.merge(Device(**device_entry))
                session.commit()

    with Session(engine) as session:  # TODO: This query is probably redundant.
        dev = session.query(Device.device_name).first()
        session.commit()

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
                        playlist_uri=plan.playlist_uri,
                        start_day=plan.start_day,
                        start_time=plan.start_time,
                    ).delete()
                    session.commit()
                raise st.experimental_rerun()


# Application

engine = create_engine(
    "sqlite:///5l.db", echo=False, future=True
)  # TODO: Check if this can be run only once..

load_dotenv()  # take environment variables from .env.

st.set_page_config(layout="wide")  # This needs to be the 1st streamlit call.

initialize_session_variables(st=st)

url_params = st.experimental_get_query_params()
sp = sign_in(st=st, url_params=url_params)
if st.session_state["signed_in"]:
    authenticated(spotify=sp)
