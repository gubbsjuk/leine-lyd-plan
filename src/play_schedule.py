import argparse
import datetime
import time

import schedule
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from constants import SCOPES
from models.db import Device, Schedule
from spotipy_utils import SQLiteCacheHandler


load_dotenv()  # take environment variables from .env.


def play(spotify, playlist_uri, device=None):
    spotify.start_playback(device_id=device, context_uri=playlist_uri)


def setup_play(user_uri, playlist_uri):
    with Session(engine) as session:
        device = (
            session.query(Device.device_id).where(Device.user_uri == user_uri).first()
        )
        session.commit()

    oauth = SpotifyOAuth(
        scope=SCOPES,
        cache_handler=SQLiteCacheHandler(username=user_uri, db_path="5l.db"),
        open_browser=False,
    )  # TODO: move db to constants.py
    spotify = spotipy.Spotify(auth_manager=oauth)

    if device:
        print("Starting playback on device:" + device[0])
        play(spotify=spotify, playlist_uri=playlist_uri, device=device[0])


def check_for_update_in_table(session, table):

    last_updated_response = (
        session.query(table.last_updated).order_by(table.last_updated.desc()).first()
    )

    if last_updated_response is not None:
        return last_updated_response[0]

    return datetime.datetime(1970, 1, 1)  # TODO: Fix this hack.


def main(engine, update_interval):
    last_updated = datetime.datetime(1970, 1, 1)
    last_updated_from_db = last_updated

    n_entries = 0
    n_entries_from_db = n_entries

    while True:
        print(
            datetime.datetime.now(), ": Looking for new playlists in schedule"
        )  # TODO: Logging
        schedule.run_pending()

        plans = []

        with Session(engine) as session:

            last_updated_from_db = check_for_update_in_table(session, Schedule)
            n_entries_from_db = session.query(Schedule.last_updated).count()

        # if nothing has changed since last time
        if (last_updated_from_db <= last_updated) and (n_entries_from_db == n_entries):
            time.sleep(update_interval)
            continue

        plans = session.query(Schedule).all()

        last_updated = last_updated_from_db
        n_entries = n_entries_from_db

        schedule.clear()
        for p in plans:
            getattr(schedule.every(), p.start_day).at(p.start_time).do(
                setup_play, user_uri=p.user_uri, playlist_uri=p.playlist_uri
            )

        print("CURRENT SCHEDULE:")
        for i, job in enumerate(schedule.get_jobs()):
            print(f"Job {i}: ", job)  # TODO: Remove this...


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=5,  # TODO: set higher
        help="Schedule refresh interval in seconds.",
    )
    args = parser.parse_args()

    engine = create_engine("sqlite:///5l.db", echo=False, future=True)

    main(engine, args.interval)
