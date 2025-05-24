from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CitySearchStat
from src.schemas import (
    GeocodingResult,
    HourlyData,
    HourlyUnits,
    WeatherResponse,
)
from src.services.search_service import process_weather_search


@pytest.fixture
def mock_geocoding_result_krasnodar():
    return GeocodingResult(
        id=542420,
        name="Krasnodar",
        latitude=45.04484,
        longitude=-38.97603,
        country_code="RU",
        country="Russia",
        admin1="Krasnodar Krai",
    )


@pytest.fixture
def mock_weather_response_krasnodar():
    return WeatherResponse(
        latitude=51.5074,
        longitude=-0.1278,
        timezone="Europe/Moscow",
        timezone_abbreviation="GMT+3",
        elevation=32.0,
        hourly_units=HourlyUnits(temperature_2m="°C"),
        hourly=HourlyData(
            time=[datetime.now(timezone.utc)],
            temperature_2m=[18.4],
            relative_humidity_2m=[66],
            apparent_temperature=[18.2],
            precipitation_probability=[0],
            weathercode=[0],
            wind_speed_10m=[5.6],
        ),
    )


@pytest.mark.asyncio
async def test_process_weather_search_success(
    mocker, mock_geocoding_result_krasnodar, mock_weather_response_krasnodar
):
    mock_get_coords = mocker.patch(
        "src.services.weather_service.get_coordinates_for_city",
        new_callable=AsyncMock,
        return_value=[mock_geocoding_result_krasnodar],
    )
    mock_get_weather = mocker.patch(
        "src.services.weather_service.get_weather_forecast",
        new_callable=AsyncMock,
        return_value=mock_weather_response_krasnodar,
    )

    mock_session = MagicMock(spec=AsyncSession)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    mock_execute_result_stat_none = MagicMock()
    mock_execute_result_stat_none.scalar_one_or_none = MagicMock(return_value=None)
    mock_session.execute = AsyncMock(return_value=mock_execute_result_stat_none)

    city_query = "London"
    user_session_id = str(uuid4())

    selected_city, weather_data, error_message = await process_weather_search(
        city_query, user_session_id, mock_session
    )

    mock_get_coords.assert_called_once_with(city_query.strip(), limit=1)
    mock_get_weather.assert_called_once_with(
        mock_geocoding_result_krasnodar.latitude,
        mock_geocoding_result_krasnodar.longitude,
    )

    assert selected_city == mock_geocoding_result_krasnodar
    assert weather_data == mock_weather_response_krasnodar
    assert error_message is None

    assert mock_session.add.call_count >= 2
    mock_session.commit.assert_called_once()
    mock_session.rollback.assert_not_called()


@pytest.mark.asyncio
async def test_process_weather_search_city_not_found(mocker):
    mock_get_coords = mocker.patch(
        "src.services.weather_service.get_coordinates_for_city",
        new_callable=AsyncMock,
        return_value=None,
    )
    mock_session = MagicMock(spec=AsyncSession)

    city_query = "UnknownCity"
    user_session_id = str(uuid4())

    selected_city, weather_data, error_message = await process_weather_search(
        city_query, user_session_id, mock_session
    )

    mock_get_coords.assert_called_once_with(city_query.strip(), limit=1)
    assert selected_city is None
    assert weather_data is None
    assert (
        error_message
        == f"Could not find '{city_query}'. Try 'City, Country Code' (e.g., Paris, FR)."
    )
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_process_weather_search_weather_not_found(
    mocker, mock_geocoding_result_krasnodar
):
    mock_get_coords = mocker.patch(
        "src.services.weather_service.get_coordinates_for_city",
        new_callable=AsyncMock,
        return_value=[mock_geocoding_result_krasnodar],
    )
    mock_get_weather = mocker.patch(
        "src.services.weather_service.get_weather_forecast",
        new_callable=AsyncMock,
        return_value=None,
    )
    mock_session = MagicMock(spec=AsyncSession)

    city_query = "London"
    user_session_id = str(uuid4())

    selected_city, weather_data, error_message = await process_weather_search(
        city_query, user_session_id, mock_session
    )

    mock_get_coords.assert_called_once_with(city_query.strip(), limit=1)
    mock_get_weather.assert_called_once_with(
        mock_geocoding_result_krasnodar.latitude,
        mock_geocoding_result_krasnodar.longitude,
    )
    assert selected_city == mock_geocoding_result_krasnodar
    assert weather_data is None
    assert (
        error_message
        == f"Could not fetch weather for {mock_geocoding_result_krasnodar.name}. Try again later."
    )
    mock_session.add.assert_not_called()
    mock_session.commit.assert_not_called()


@pytest.mark.asyncio
async def test_process_weather_search_empty_city_query():
    mock_session = MagicMock(spec=AsyncSession)
    selected_city, weather_data, error_message = await process_weather_search(
        "", "some_session_id", mock_session
    )
    assert selected_city is None
    assert weather_data is None
    assert error_message == "Please enter a city name."


@pytest.mark.asyncio
async def test_process_weather_search_updates_existing_stat(
    mocker, mock_geocoding_result_krasnodar, mock_weather_response_krasnodar
):
    mock_get_coords = mocker.patch(
        "src.services.weather_service.get_coordinates_for_city",
        new_callable=AsyncMock,
        return_value=[mock_geocoding_result_krasnodar],
    )
    mock_get_weather = mocker.patch(
        "src.services.weather_service.get_weather_forecast",
        new_callable=AsyncMock,
        return_value=mock_weather_response_krasnodar,
    )

    mock_session = MagicMock(spec=AsyncSession)
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()
    mock_session.rollback = AsyncMock()

    existing_stat = CitySearchStat(
        id=uuid4(),
        city_name=mock_geocoding_result_krasnodar.name,
        country_code=mock_geocoding_result_krasnodar.country_code,
        search_count=5,
        last_searched_at=datetime.now(timezone.utc),
    )
    mock_execute_result_stat_exists = MagicMock()
    mock_execute_result_stat_exists.scalar_one_or_none = MagicMock(
        return_value=existing_stat
    )
    mock_session.execute = AsyncMock(return_value=mock_execute_result_stat_exists)

    city_query = "London"
    user_session_id = str(uuid4())

    await process_weather_search(city_query, user_session_id, mock_session)

    assert existing_stat.search_count == 6
    mock_session.commit.assert_called_once()
