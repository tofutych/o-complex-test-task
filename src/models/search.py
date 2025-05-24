from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class CitySearchStat(Base):
    city_name: Mapped[str] = mapped_column(
        String(255),
        index=True,
    )
    country_code: Mapped[str | None] = mapped_column(
        String(10),
        index=True,
        nullable=True,
    )
    search_count: Mapped[int] = mapped_column(
        Integer,
        default=1,
    )
    last_searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )


class SearchHistoryLog(Base):
    user_session_id: Mapped[str] = mapped_column(
        String(36),
        index=True,
    )
    city_name: Mapped[str] = mapped_column(String(255))
    country_code: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
    )
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.now(timezone.utc),
    )
