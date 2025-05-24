from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CitySearchStat, SearchHistoryLog


async def get_city_search_stats(
    session: AsyncSession, limit: int = 10, offset: int = 0
):
    stmt = (
        select(CitySearchStat)
        .order_by(
            CitySearchStat.search_count.desc(),
            CitySearchStat.last_searched_at.desc(),
        )
        .limit(limit)
        .offset(offset)
    )
    results = await session.execute(stmt)
    return results.scalars().all()


async def get_my_search_history(
    session: AsyncSession, user_session_id: str, limit: int = 20
):
    stmt = (
        select(SearchHistoryLog)
        .where(SearchHistoryLog.user_session_id == user_session_id)
        .order_by(
            SearchHistoryLog.searched_at.desc(),
        )
        .limit(limit)
    )
    results = await session.execute(stmt)
    return results.scalars().all()
