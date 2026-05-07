from langchain.tools import tool
import os
from dotenv import load_dotenv
import requests
from src.log_config import logger
from src.model_tool.schema import (
    CityWeatherInput,
    CityWeatherOutput,
    CityDailyForecastInput,
    CityDailyForecastOutput,
    ForecastStep,
)
from src.model_tool.util import _get_country_code, _get_city_data

# Carica le variabili d'ambiente (in particolare OPENWEATHER_API_KEY)
load_dotenv()


@tool(args_schema=CityWeatherInput)
def get_current_temperature(
    city: str, country: str, state: str = "", units: str = "Celsius"
) -> CityWeatherOutput:
    """Get the current temperature in a city."""
    # Tool di esempio: ottiene la temperatura attuale tramite l'API di OpenWeather.
    logger.info(
        f"Getting current temperature with parameters: city={city}, state={state}, country={country}, units={units}"
    )

    # Conversione del nome del paese in codice ISO (richiesto da OpenWeather)
    iso_code = _get_country_code(country)
    if iso_code is None:
        return None

    # Geocoding: dalla città si ottengono latitudine e longitudine
    latitude, longitude = _get_city_data(city, state, iso_code)
    if latitude is None or longitude is None:
        return None

    # Parametri della chiamata all'endpoint /weather
    params = {
        "lat": latitude,
        "lon": longitude,
        "appid": os.getenv("OPENWEATHER_API_KEY"),
        # OpenWeather usa "metric"/"imperial"; mappiamo la richiesta dell'utente
        "units": "metric" if units == "Celsius" else "imperial",
    }

    try:
        # Chiamata HTTP all'API meteo
        weather_data = requests.get(
            "https://api.openweathermap.org/data/2.5/weather", params=params
        )
        logger.info(f"Weather data: {weather_data.json()}")
        weather_data.raise_for_status()
        weather_data = weather_data.json()
    except requests.exceptions.RequestException as e:
        # In caso di errore di rete o HTTP, logghiamo e ritorniamo None
        logger.error(f"Errore durante il recupero dei dati meteo della città {city}: {e}")
        return None

    # Costruzione dell'oggetto di output tipizzato (Pydantic)
    return CityWeatherOutput(
        city=city,
        country=country,
        state=state,
        temperature=weather_data["main"]["temp"],
        weather=weather_data["weather"][0]["description"],
    )


@tool(args_schema=CityDailyForecastInput)
def get_daily_forecast(
    city: str, country: str, steps: int, state: str = "", units: str = "Celsius"
) -> CityDailyForecastOutput:
    """Get the daily forecast for a city."""
    # Tool di esempio: ottiene previsioni a step di 3h tramite OpenWeather.
    logger.info(
        f"Getting daily forecast with parameters: city={city}, state={state}, country={country}, units={units}, steps={steps}"
    )

    # Anche qui serve il codice ISO del paese
    iso_code = _get_country_code(country)
    if iso_code is None:
        return None

    # Geocoding della città
    latitude, longitude = _get_city_data(city, state, iso_code)
    if latitude is None or longitude is None:
        return None

    # Parametri per l'endpoint /forecast: cnt è il numero di step richiesti
    params = {
        "lat": latitude,
        "lon": longitude,
        "cnt": steps,
        "units": "metric" if units == "Celsius" else "imperial",
        "appid": os.getenv("OPENWEATHER_API_KEY"),
    }
    try:
        forecast_data = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast", params=params
        )
        logger.info(f"Forecast data: {forecast_data.json()}")
        forecast_data.raise_for_status()
        forecast_data = forecast_data.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante il recupero dei dati meteo della città {city}: {e}")
        return None

    # Mappatura della lista di previsioni grezze in oggetti ForecastStep tipizzati
    return CityDailyForecastOutput(
        city=city,
        country=country,
        state=state,
        forecasts=[
            ForecastStep(
                timestamp=step["dt_txt"],
                temperature_min=step["main"]["temp_min"],
                temperature_max=step["main"]["temp_max"],
                weather=step["weather"][0]["description"],
            )
            for step in forecast_data["list"]
        ],
    )


# Lista dei tool resi disponibili all'agent.
# NB: questi tool sono solo a scopo dimostrativo; l'idea è mostrare COME
# si registrano dei tool LangChain, non fornire un servizio meteo reale.
tools = [get_current_temperature, get_daily_forecast]


if __name__ == "__main__":
    # Piccolo test manuale dei tool (eseguibile con `python -m src.model_tool.tool`)
    print(get_current_temperature.invoke({"city": "New York", "state": "New York", "country": "USA"}))
    print(
        get_daily_forecast.invoke(
            {"city": "New York", "state": "New York", "country": "USA", "units": "Celsius", "steps": 4}
        )
    )
