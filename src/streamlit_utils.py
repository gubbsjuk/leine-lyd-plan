import streamlit as st

from spotipy.cache_handler import CacheHandler


class StreamlitCacheHandler(CacheHandler):
    """
    A cache handler that stores the token info in a Streamlit session.
    """

    def get_cached_token(self):
        return st.session_state.get("token_info", None)

    def save_token_to_cache(self, token_info):
        st.session_state["token_info"] = token_info
