import os

import spotipy


# from spotipy.oauth2 import SpotifyOAuth


# Gets a oath token from supplied auth-code. Removes cache. Returns token, or -1 on failure. #TODO: Implement failure.
def get_token(oauth, code):
    token = oauth.get_access_token(code, as_dict=False, check_cache=False)

    # remove cached token saved in directory #TODO: Why?
    os.remove(".cache")

    # return the token
    return token


# Authenticates with Spotify API. Returns spotipy API object.
def sign_in(token):
    sp = spotipy.Spotify(auth=token)
    return sp


# Tries to validate token with spotify. Puts validated token in session_state["cached_token"]
def app_get_token(st):
    try:
        token = get_token(st.session_state["oauth"], st.session_state["code"])
    except Exception as e:
        st.error("An error occurred during token retrieval!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["cached_token"] = token


# Streamlit func to authenticate with spotify. Uses cached token. Throws Exception.
# Takes parameters:
#   st, Streamlit app.
#   success_func, function to be called when successfull
#   returns spotipy object.
def app_sign_in(st, success_func):
    try:
        sp = sign_in(st.session_state["cached_token"])
    except Exception as e:
        st.error("An error occurred during sign-in!")
        st.write("The error is as follows:")
        st.write(e)
    else:
        st.session_state["signed_in"] = True
        success_func()
        st.success("Sign in success!")

    return sp
