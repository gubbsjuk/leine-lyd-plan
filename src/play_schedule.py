import argparse
import datetime
import time

import schedule
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import and_, create_engine
from sqlalchemy.orm import Session

from constants import DB_PATH, SCOPES
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

    oauth = SpotifyOAuth(
        scope=SCOPES,
        cache_handler=SQLiteCacheHandler(username=user_uri, db_path=DB_PATH),
        open_browser=False,
    )
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

    while True:
        print(
            datetime.datetime.now(), ": Looking for new playlists in schedule"
        )  # TODO: Logging

        print("CURRENT SCHEDULE:")
        for i, job in enumerate(schedule.get_jobs()):
            print(f"Job {i}: ", job)  # TODO: Remove this...
        schedule.run_pending()

        plans = []

        with Session(engine) as session:

            last_updated_from_db = check_for_update_in_table(session, Schedule)

        # if nothing has changed since last time
        if last_updated_from_db <= last_updated:
            time.sleep(update_interval)
            continue

        plans = (
            session.query(Schedule).filter(Schedule.last_updated > last_updated).all()
        )

        last_updated = last_updated_from_db

        for p in plans:
            if p.to_delete:
                schedule.clear(p.schedule_id)
                session.query(Schedule).where(
                    and_(
                        Schedule.schedule_id == p.schedule_id,
                        Schedule.to_delete == True,  # NOQA
                    )
                ).delete()
                session.commit()
                print("Deleted job: " + p.schedule_id)
            else:
                getattr(schedule.every(), p.start_day).at(p.start_time).do(
                    setup_play, user_uri=p.user_uri, playlist_uri=p.playlist_uri
                ).tag(p.schedule_id)


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

    engine = create_engine("sqlite:///" + DB_PATH, echo=False, future=True)

    main(engine, args.interval)
