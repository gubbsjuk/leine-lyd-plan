import datetime  # TODO: Remove
import time

import schedule
import spotipy

from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth

from constants import CONFIG_PATH, PLAN_PATH
from utils import load_json, write_json


load_dotenv()  # take environment variables from .env.


def play(spotify, playlist_id):
    config = load_json(CONFIG_PATH, {})
    spotify.start_playback(device_id=config["device_id"], context_uri=playlist_id)


def main(spotify):
    while True:
        print(datetime.datetime.now())
        plans = load_json(PLAN_PATH)
        schedule.run_pending()
        time.sleep(10)  # TODO: Set to something meaningful

        if not plans["updated"]:
            print("not updated...")
            continue

        schedule.clear()
        for p in plans["plans"]:
            day = p["start_day"].lower()
            getattr(schedule.every(), day).at(p["start_time"]).do(
                play, spotify=spotify, playlist_id=p["playlist_id"]
            )
        print(schedule.get_jobs())
        plans["updated"] = False
        write_json(PLAN_PATH, plans)


if __name__ == "__main__":
    spotify = spotipy.Spotify(
        client_credentials_manager=SpotifyOAuth(scope=["user-modify-playback-state"])
    )
    main(spotify)
