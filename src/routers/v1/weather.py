from datetime import timedelta
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Form,
    Request,
)
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import (
    db_manager,
    settings,
    templates,
)
from src.services import search_service, weather_service
from src.utils import get_or_create_session_id

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.post("/search", response_class=HTMLResponse, name="search_weather_htmx")
async def search_weather_htmx(
    request: Request,
    city: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(db_manager.get_async_session)],
    user_session_id: Annotated[str, Depends(get_or_create_session_id)],
):
    (
        selected_city,
        weather_data,
        error_message,
    ) = await search_service.process_weather_search(
        city_query=city, user_session_id=user_session_id, session=session
    )

    if error_message:
        return templates.TemplateResponse(
            "partials/weather_results.html",
            {
                "request": request,
                "city_info": selected_city,
                "error_message": error_message,
            },
        )

    context = {
        "request": request,
        "city_info": selected_city,
        "weather": weather_data,
        "get_weather_description": weather_service.get_weather_description,
        "hourly_forecast_limit": 24,
    }
    template_resp = templates.TemplateResponse("partials/weather_results.html", context)

    cookie_value = f"{selected_city.name},{selected_city.country or ''}"  # pyright: ignore [reportOptionalMemberAccess]
    if selected_city:
        country_identifier = selected_city.country_code or selected_city.country or ""
        cookie_value = f"{selected_city.name},{country_identifier}"
        template_resp.set_cookie(
            key=settings.RECENT_CITY_COOKIE_NAME,
            value=cookie_value,
            max_age=int(timedelta(days=30).total_seconds()),
            httponly=True,
            samesite="lax",
        )

    return template_resp


@router.get(
    "/autocomplete-city", response_class=HTMLResponse, name="autocomplete_city_htmx"
)
async def autocomplete_city_suggestions(request: Request, city: str | None = ""):
    if not city or len(city.strip()) < 2:
        return HTMLResponse("")

    geo_results = await weather_service.get_coordinates_for_city(city.strip(), limit=7)
    return templates.TemplateResponse(
        "partials/city_suggestions.html",
        {"request": request, "suggestions": geo_results or []},
    )
