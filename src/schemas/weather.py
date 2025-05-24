from datetime import datetime
from typing import Any

from pydantic import (
    Field,
    field_validator,
)

from .base import AppBaseModel


class GeocodingResult(AppBaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    country_code: str | None = None
    country: str | None = None
    admin1: str | None = None


class GeocodingResponse(AppBaseModel):
    results: list[GeocodingResult] | None = None


class HourlyUnits(AppBaseModel):
    temperature_2m: str | None = Field(default=None, alias="temperature_2m")
    relative_humidity_2m: str | None = Field(default=None, alias="relative_humidity_2m")
    apparent_temperature: str | None = Field(default=None, alias="apparent_temperature")
    precipitation_probability: str | None = Field(
        default=None, alias="precipitation_probability"
    )
    weather_code: str | None = Field(default=None, alias="weathercode")
    wind_speed_10m: str | None = Field(default=None, alias="wind_speed_10m")


class HourlyData(AppBaseModel):
    time: list[datetime]
    temperature_2m: list[float | None] | None = Field(
        default=None, alias="temperature_2m"
    )
    relative_humidity_2m: list[int | None] | None = Field(
        default=None, alias="relative_humidity_2m"
    )
    apparent_temperature: list[float | None] | None = Field(
        default=None, alias="apparent_temperature"
    )
    precipitation_probability: list[int | None] | None = Field(
        default=None, alias="precipitation_probability"
    )
    weather_code: list[int | None] | None = Field(default=None, alias="weathercode")
    wind_speed_10m: list[float | None] | None = Field(
        default=None, alias="wind_speed_10m"
    )

    @field_validator(
        "temperature_2m",
        "relative_humidity_2m",
        "apparent_temperature",
        "precipitation_probability",
        "weather_code",
        "wind_speed_10m",
        mode="before",
    )
    @classmethod
    def none_string_to_none_for_hourly_data(cls, v: Any) -> Any | None:
        if isinstance(v, str) and v == "None":
            return None
        return v


class WeatherResponse(AppBaseModel):
    latitude: float
    longitude: float
    timezone: str
    timezone_abbreviation: str
    elevation: float
    hourly_units: HourlyUnits
    hourly: HourlyData
