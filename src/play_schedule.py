import argparse
import datetime  # TODO: Remove
import time

import schedule
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models.schedule import Schedule


load_dotenv()  # take environment variables from .env.


def play(spotify, playlist_id):  # TODO: Set device id from db(?)
    spotify.start_playback(
        device_id="5b81dca57efb9ead5c69c4e4dd85e8d33d7b4977", context_uri=playlist_id
    )


def main(spotify, engine, update_interval):
    last_updated = datetime.datetime(1970, 1, 1)
    last_updated_from_db = last_updated

    n_entries = 0
    n_entries_from_db = n_entries

    while True:
        print(datetime.datetime.now(), ": Looking for new playlists in schedule")
        schedule.run_pending()

        plans = []

        with Session(engine) as session:
            last_updated_response = (
                session.query(Schedule.last_updated)
                .order_by(Schedule.last_updated.desc())
                .first()
            )

            if last_updated_response is not None:
                last_updated_from_db = last_updated_response[0]

            n_entries_from_db = session.query(Schedule.last_updated).count()  # TODO: On
            print(f"{n_entries_from_db=}", f"{n_entries=}")

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
                play, spotify=spotify, playlist_id=p.playlist_id
            )

        print("CURRENT SCHEDULE:")
        for i, job in enumerate(schedule.get_jobs()):
            print(f"Job {i}: ", job)  # TODO: Remove this...


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        default=60,
        help="Schedule refresh interval in seconds",
    )
    args = parser.parse_args()

    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyOAuth(scope=["user-modify-playback-state"])
    )
    engine = create_engine("sqlite:///5l.db", echo=False, future=True)

    main(spotify, engine, args.interval)
