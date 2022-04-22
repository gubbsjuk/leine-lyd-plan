import json
import logging
import os
import sqlite3

import streamlit as st

from spotipy.cache_handler import CacheHandler
from spotipy.util import CLIENT_CREDS_ENV_VARS


logger = logging.getLogger(__name__)


class StreamlitCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in a Streamlit session.
    """

    def get_cached_token(self):
        return st.session_state.get("token_info", None)

    def save_token_to_cache(self, token_info):
        st.session_state["token_info"] = token_info


class SQLiteCacheHandler(CacheHandler):
    """
    Handles reading and writing cached Spotify authorization tokens
    as json to a SQLite table using the Python built-in sqlite3.
    """

    def __init__(self, username=None, db_path="cache.db"):
        """
        Parameters:
             * db_path: The path to the sqlite database. A database will be
             created if none exists on this path.
             * username: May be supplied or set as environment variable,
             otherwise generated. (Will be used as the key for the
             entry).
        """
        self.db_path = db_path
        self.username = (
            username
            or os.getenv(CLIENT_CREDS_ENV_VARS["client_username"])
            or "someUserNameThatDoesNotExistInSpotify"
        )
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()
        cur.execute(
            "CREATE TABLE IF NOT EXISTS token_info (key TEXT PRIMARY KEY, value TEXT);"
        )
        con.commit()
        con.close()

    def get_cached_token(self):
        token_info = None

        try:
            con = sqlite3.connect(self.db_path)
            cur = con.cursor()
            token_info_json = cur.execute(
                "SELECT value FROM token_info WHERE key=?", (self.username,)
            ).fetchone()
            con.close()
            if token_info_json:
                return json.loads(token_info_json[0])

        except sqlite3.Error as error:
            logger.warning("An error occurred:", error.args[0])

        return token_info

    def save_token_to_cache(self, token_info):
        con = sqlite3.connect(self.db_path)
        try:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO token_info VALUES (?, ?)",
                (self.username, json.dumps(token_info)),
            )
            con.commit()
        except sqlite3.Error as error:
            logger.warning("An error occurred:", error.args[0])
        finally:
            con.close()
