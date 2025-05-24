import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    Request,
)
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core import (
    db_manager,
    templates,
)
from src.schemas import CityStatPublic, SearchLogPublic
from src.services import statistics_service
from src.utils import get_or_create_session_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/statistics", tags=["Statistics"])


@router.get(
    "/stats/city-searches",
    response_model=list[CityStatPublic],
    name="get_city_search_stats",
)
async def api_get_city_search_stats(
    session: Annotated[AsyncSession, Depends(db_manager.get_async_session)],
    limit: int = 10,
    offset: int = 0,
):
    return await statistics_service.get_city_search_stats(session, limit, offset)


@router.get(
    "/history/my-searches",
    response_model=list[SearchLogPublic],
    name="get_my_search_history",
)
async def api_get_my_search_history(
    user_session_id: Annotated[str, Depends(get_or_create_session_id)],
    session: Annotated[AsyncSession, Depends(db_manager.get_async_session)],
    limit: int = 20,
):
    return await statistics_service.get_my_search_history(
        session, user_session_id, limit
    )


@router.get("/search-statistics", response_class=HTMLResponse, name="search_stats_page")
async def get_search_stats_page(request: Request):
    try:
        api_overall_stats_url = request.url_for("get_city_search_stats")
        api_my_history_url = request.url_for("get_my_search_history")
    except Exception as e:
        logger.error(f"Something went wrong: {e}")
        api_overall_stats_url = ""
        api_my_history_url = ""

    return templates.TemplateResponse(
        "search_stats_dashboard.html",
        {
            "request": request,
            "title": "Статистика поиска",
            "api_overall_stats_url": api_overall_stats_url,
            "api_my_history_url": api_my_history_url,
        },
    )
