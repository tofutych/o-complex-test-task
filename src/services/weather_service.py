import logging

import httpx

from src.core.config import settings
from src.schemas import (
    GeocodingResponse,
    GeocodingResult,
    WeatherResponse,
)

logger = logging.getLogger(__name__)

WMO_WEATHER_CODES = {
    0: "Ясно",
    1: "Преимущественно ясно",
    2: "Переменная облачность",
    3: "Пасмурно",
    45: "Туман",
    48: "Осаждающий изморозь",
    51: "Морось: Легкая",
    53: "Морось: Умеренная",
    55: "Морось: Сильная",
    56: "Замерзающая морось: Легкая",
    57: "Замерзающая морось: Сильная",
    61: "Дождь: Легкий",
    63: "Дождь: Умеренный",
    65: "Дождь: Сильный",
    66: "Замерзающий дождь: Легкий",
    67: "Замерзающий дождь: Сильный",
    71: "Снегопад: Легкий",
    73: "Снегопад: Умеренный",
    75: "Снегопад: Сильный",
    77: "Снежные зерна",
    80: "Ливни: Легкие",
    81: "Ливни: Умеренные",
    82: "Ливни: Сильные",
    85: "Снеговые ливни: Легкие",
    86: "Снеговые ливни: Сильные",
    95: "Гроза: Легкая или умеренная",
    96: "Гроза с небольшим градом",
    99: "Гроза с сильным градом",
}


async def get_coordinates_for_city(
    city_name: str, limit: int = 5
) -> list[GeocodingResult] | None:
    async with httpx.AsyncClient() as client:
        params = {"name": city_name, "count": limit, "language": "en", "format": "json"}
        try:
            response = await client.get(str(settings.GEOCODING_API_URL), params=params)
            _ = response.raise_for_status()
            data = GeocodingResponse.model_validate(response.json())
            return data.results
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP error fetching coordinates for {city_name}: {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(f"Request error fetching coordinates for {city_name}: {e}")
        except Exception as e:
            logger.error(f"Error parsing coordinates response for {city_name}: {e}")
        return None


async def get_weather_forecast(
    latitude: float, longitude: float
) -> WeatherResponse | None:
    async with httpx.AsyncClient() as client:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,weathercode,wind_speed_10m",
            "forecast_days": 1,
            "timezone": "auto",
        }
        try:
            response = await client.get(str(settings.WEATHER_API_URL), params=params)
            _ = response.raise_for_status()
            return WeatherResponse.model_validate(response.json())
        except httpx.HTTPStatusError as e:
            logger.error(
                f"HTTP Status error fetching weather for ({latitude},{longitude}): {e.response.status_code} - {e.response.text}"
            )
        except httpx.RequestError as e:
            logger.error(
                f"Request Error fetching weather for ({latitude},{longitude}): {e}"
            )
        except Exception as e:
            logger.error(
                f"Error parsing weather response for ({latitude},{longitude}): {e}"
            )
        return None


def get_weather_description(code: int | None) -> str:
    if code is None:
        logger.debug(f"No data for {code=}")
        return "Data not available"
    return WMO_WEATHER_CODES.get(code, "Unknown")
