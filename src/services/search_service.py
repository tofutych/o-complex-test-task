from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CitySearchStat, SearchHistoryLog
from src.schemas import GeocodingResult, WeatherResponse
from src.services import weather_service


async def process_weather_search(
    city_query: str,
    user_session_id: str,
    session: AsyncSession,
) -> tuple[GeocodingResult | None, WeatherResponse | None, str | None]:
    if not city_query or not city_query.strip():
        return None, None, "Please enter a city name."

    geo_results = await weather_service.get_coordinates_for_city(
        city_query.strip(), limit=1
    )
    if not geo_results or not geo_results[0]:
        return (
            None,
            None,
            f"Could not find '{city_query}'. Try 'City, Country Code' (e.g., Paris, FR).",
        )

    selected_city = geo_results[0]
    weather_data = await weather_service.get_weather_forecast(
        selected_city.latitude, selected_city.longitude
    )

    if not weather_data:
        return (
            selected_city,
            None,
            f"Could not fetch weather for {selected_city.name}. Try again later.",
        )

    try:
        log_entry = SearchHistoryLog(
            user_session_id=user_session_id,
            city_name=selected_city.name,
            country_code=selected_city.country_code,
            latitude=selected_city.latitude,
            longitude=selected_city.longitude,
        )
        session.add(log_entry)

        stmt = select(CitySearchStat).where(
            CitySearchStat.city_name == selected_city.name,
            CitySearchStat.country_code == selected_city.country_code,
        )
        result = await session.execute(stmt)
        db_stat = result.scalar_one_or_none()

        current_time_utc = datetime.now(timezone.utc)
        if db_stat:
            db_stat.search_count += 1
            db_stat.last_searched_at = current_time_utc
            session.add(db_stat)
        else:
            new_stat = CitySearchStat(
                city_name=selected_city.name,
                country_code=selected_city.country_code,
                last_searched_at=current_time_utc,
            )
            session.add(new_stat)
        await session.commit()
    except Exception as e:
        await session.rollback()

    return selected_city, weather_data, None
