# Leine lyds lille liste-løsning
Også kalt `5L` (utales "feml")

## Bruk
For å kjøre denne løsningen trenger du `poetry` (og pyenv?).

Når du har `poetry` installert gir følgende kommando deg et virtuelt miljø med alt du trenger
```py
poetry install
```

Konfigurer miljøvariabler (eller `.env`-fil) til å ha
```sh
SPOTIPY_CLIENT_ID=din_spotify_client_id
SPOTIPY_CLIENT_SECRET=din_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8501
```

Når du henter client info fra [Spotify Dashboard](https://developer.spotify.com/dashboard/), må du også konfigurere `Redirect URIs` til å inneholde samme redirect URI som over.

For å kjøre applikasjonen
```py
poetry run streamlit run src/app.py
```

Nå vil den be deg om å autentisere med Spotify og gi riktige

## Komponenter
* [Spotipy](https://spotipy.readthedocs.io/en/2.19.0/)
Python SDK for Spotify Web API. [Here](https://developer.spotify.com/console/) is a great way explore the API when developing!

* [Streamlit](https://docs.streamlit.io/library/get-started)
Dashboarding (UI) tool
