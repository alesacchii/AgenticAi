from pydantic import BaseModel, Field

# Gli schemi Pydantic definiscono il "contratto" di input/output dei tool.
# LangChain li usa per generare automaticamente la signature che il modello
# deve rispettare quando decide di invocare un tool.


class CityWeatherInput(BaseModel):
    """Schema di input per le query sulla temperatura attuale."""

    # Il nome della città deve essere in inglese per essere riconosciuto dall'API
    city: str = Field(description="City name in english (for example Rome instead of Roma)")
    # Lo stato è significativo solo per gli USA (es. "New York")
    state: str = Field(
        description="State name in english and use it only if the country is United States",
        default="",
    )
    country: str = Field(description="Country name in english (for example United States of America or USA)")
    # Unità di misura: l'utente può chiedere Celsius o Fahrenheit
    units: str = Field(
        description="Units of temperature (for example Celsius or Fahrenheit) use it only if the user ask it",
        default="Celsius",
    )


class CityWeatherOutput(BaseModel):
    """Schema di output con i dati meteo correnti restituiti al modello."""

    city: str = Field(description="City name in english")
    country: str = Field(description="Country name in english")
    state: str = Field(description="State name in english and use it only if the country is United States")
    temperature: float = Field(description="Temperature in Celsius")
    weather: str = Field(description="Weather description in english")


class CityDailyForecastInput(BaseModel):
    """Schema di input per le query sulle previsioni a più step."""

    city: str = Field(description="City name in english (for example Rome instead of Roma)")
    state: str = Field(
        description="State name in english and use it only if the country is United States",
        default="",
    )
    country: str = Field(description="Country name in english (for example United States of America or USA)")
    units: str = Field(
        description="Units of temperature (for example Celsius or Fahrenheit) use it only if the user ask it",
        default="Celsius",
    )
    # Vincolo numerico: l'API consente da 1 a 16 step da 3h ciascuno
    steps: int = Field(
        ge=1,
        le=16,
        description="Steps of forecast in numbers of 3h from today, example: 1 for 3h from now, 2 for 6h from now, 3 for 9h from now, etc.",
    )


class ForecastStep(BaseModel):
    """Singolo step della previsione (intervallo da 3 ore)."""

    timestamp: str = Field(description="Timestamp of the forecast")
    temperature_min: float
    temperature_max: float
    weather: str


class CityDailyForecastOutput(BaseModel):
    """Schema di output: la lista di step previsionali per una città."""

    city: str = Field(description="City name in english")
    country: str = Field(description="Country name in english")
    state: str = Field(description="State name in english and use it only if the country is United States")
    forecasts: list[ForecastStep] = Field(description="List of daily forecasts")
