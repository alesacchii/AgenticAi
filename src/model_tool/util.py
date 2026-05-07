import pandas as pd
import requests
from dotenv import load_dotenv
import os
from src.log_config import logger

# Carica la variabile OPENWEATHER_API_KEY dal file .env
load_dotenv()


def _get_country_code(country: str):
    """Restituisce il codice ISO 3166-2 del paese a partire dal nome.

    L'API di OpenWeather richiede il codice ISO; il nome scritto dall'utente
    può essere in forma estesa, alpha-2 o alpha-3. La funzione cerca su tutte
    e tre le colonne del CSV di lookup e ritorna la prima corrispondenza.
    """
    try:
        # Caricamento della tabella di lookup dei codici paese
        country_data = pd.read_csv("src/data/country_iso.csv")
        try:
            # Tentativo di match su più colonne (nome, codice 2 lettere, codice 3 lettere)
            for col in ["name", "alpha-2", "alpha-3"]:
                match = country_data.loc[country_data[col] == country, "iso_3166-2"]
                if not match.empty:
                    iso_code = match.iloc[0]
                    break
        except Exception as e:
            logger.error(f"Errore durante la ricerca del codice ISO del paese: {e}")
            return None

        logger.info(f"Country code: {iso_code}")
        return iso_code
    except Exception as e:
        # Errore generico (es. CSV non trovato)
        logger.error(f"Errore durante la ricerca del codice ISO del paese: {e}")
        return None


def _get_city_data(city: str, state: str, country: str):
    """Esegue il geocoding di una città e ne restituisce (latitudine, longitudine).

    Usa l'API geo di OpenWeather, che accetta una stringa nel formato
    "città,stato,paese". Lo stato è opzionale (utile soprattutto per gli USA).
    """
    try:
        # Parametri per l'endpoint di geocoding diretto
        params = {
            "q": f"{city},{state},{country}",
            "appid": os.getenv("OPENWEATHER_API_KEY"),
            "limit": 1,  # ci basta il primo risultato
        }
        try:
            city_data = requests.get(
                "http://api.openweathermap.org/geo/1.0/direct", params=params
            )
            city_data.raise_for_status()
            city_data = city_data.json()
        except requests.exceptions.RequestException as e:
            # Errori di rete / HTTP
            logger.error(f"Errore durante il recupero dei dati della città: {e}")
            return None

        # L'API ritorna una lista vuota se la città non viene trovata
        if not city_data:
            logger.error(f"Città '{city}' non trovata.")
            return None

        # Estrazione delle coordinate dal primo risultato
        latitude = city_data[0]["lat"]
        longitude = city_data[0]["lon"]

        return latitude, longitude
    except Exception as e:
        logger.error(f"Errore durante il recupero dei dati della città: {e}")
        return None
