# Leine lyds lille liste-løsning
Også kalt `5L` (utales "feml")

## TODO
- [x] UI to generate plan + config
- [x] App to read plan, schedule and run on spotify
- [x] Fix read/write collisions (sometimes buggy...)
- [x] Multi-user
- [ ] Robust auth

## Bruk
For å kjøre denne løsningen trenger du `poetry` (og pyenv?).

Når du har `poetry` installert gir følgende kommando deg et virtuelt miljø med alt du trenger
```sh
poetry install
```

Konfigurer miljøvariabler (eller `.env`-fil) til å ha
```sh
SPOTIPY_CLIENT_ID=din_spotify_client_id
SPOTIPY_CLIENT_SECRET=din_spotify_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8501
```

Når du henter client info fra [Spotify Dashboard](https://developer.spotify.com/dashboard/), må du også konfigurere `Redirect URIs` til å inneholde samme redirect URI som over.

Sett opp databasen ved å kjøre
```sh
poetry run python src/setup_db.py
```


For å kjøre applikasjonen, kjør disse i to forskjellige vinduer:
```sh
poetry run streamlit run src/app.py
```
```sh
poetry run python src/play_schedule.py
```

Nå vil den be deg om å autentisere med Spotify og gi riktige

## Bidra
Akkurat som å bruke den, men kjør også følgende kommando for å installere `pre-commit`-hooks slik at koden automatisk kontrolleres (og eventuelt fikses) for stil, ubrukte imports, o.l. på hver `git commit`
```sh
poetry run pre-commit install
```

## Komponenter
#### [Spotipy](https://spotipy.readthedocs.io/en/2.19.0/)
Python SDK for Spotify Web API. [Here](https://developer.spotify.com/console/) is a great way explore the API when developing!

#### [Streamlit](https://docs.streamlit.io/library/get-started)
Dashboarding (UI) tool
