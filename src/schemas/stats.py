import uuid
from datetime import datetime

from .base import AppBaseModel


class CityStatPublic(AppBaseModel):
    id: uuid.UUID
    city_name: str
    country_code: str | None = None
    search_count: int
    last_searched_at: datetime


class SearchLogPublic(AppBaseModel):
    id: uuid.UUID
    user_session_id: str
    city_name: str
    country_code: str | None = None
    latitude: float
    longitude: float
    searched_at: datetime


class CityChartDataPoint(AppBaseModel):
    city_name: str
    country_code: str | None = None
    search_count: int
