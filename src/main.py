import logging
from contextlib import asynccontextmanager

from fastapi import (
    Cookie,
    FastAPI,
    Request,
)
from fastapi.staticfiles import StaticFiles

from src.core import (
    db_manager,
    settings,
    templates,
)
from src.models import Base
from src.routers import api_v1_router
from src.utils import parse_recent_city_cookie, prepare_static_dirs

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):  # pyright: ignore [reportUnusedParameter]
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await db_manager.dispose()


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

app.include_router(api_v1_router, prefix=settings.API_V1_STR)

static_dir = prepare_static_dirs()
app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/api/v1/weather/ui", tags=["Weather"])
@app.get("/", include_in_schema=False)
async def read_root(
    request: Request,
    recent_city_cookie: str | None = Cookie(  # pyright: ignore [reportCallInDefaultInitializer]
        None,
        alias=settings.RECENT_CITY_COOKIE_NAME,
    ),
):
    recent_city_info = parse_recent_city_cookie(recent_city_cookie)
    if not recent_city_cookie:
        logger.warning(f"Cookie слишком короткий {recent_city_cookie=}")

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "Weather App",
            "recent_city_info": recent_city_info,
            "settings": settings,
        },
    )
