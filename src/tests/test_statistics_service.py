from datetime import datetime, timezone
from unittest.mock import (
    AsyncMock,
    MagicMock,
)
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import CitySearchStat, SearchHistoryLog
from src.services.statistics_service import get_city_search_stats, get_my_search_history


@pytest.mark.asyncio
async def test_get_city_search_stats():
    mock_session = MagicMock(spec=AsyncSession)
    mock_execute_result = MagicMock()

    mock_stat_1 = CitySearchStat(
        id=uuid4(),
        city_name="London",
        search_count=10,
        last_searched_at=datetime.now(timezone.utc),
    )
    mock_stat_2 = CitySearchStat(
        id=uuid4(),
        city_name="Paris",
        search_count=5,
        last_searched_at=datetime.now(timezone.utc),
    )
    expected_stats_list = [mock_stat_1, mock_stat_2]

    mock_execute_result.scalars = MagicMock()
    mock_execute_result.scalars.return_value.all = MagicMock(
        return_value=expected_stats_list
    )
    mock_session.execute = AsyncMock(return_value=mock_execute_result)

    limit = 5
    offset = 0
    returned_stats = await get_city_search_stats(
        mock_session, limit=limit, offset=offset
    )

    mock_session.execute.assert_called_once()

    assert returned_stats == expected_stats_list
    mock_execute_result.scalars.assert_called_once()
    mock_execute_result.scalars.return_value.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_my_search_history():
    mock_session = MagicMock(spec=AsyncSession)
    mock_execute_result = MagicMock()

    user_session_id_to_test = str(uuid4())

    mock_log_1 = SearchHistoryLog(
        id=uuid4(),
        user_session_id=user_session_id_to_test,
        city_name="Berlin",
        latitude=1.0,
        longitude=1.0,
        searched_at=datetime.now(timezone.utc),
    )
    mock_log_2 = SearchHistoryLog(
        id=uuid4(),
        user_session_id=user_session_id_to_test,
        city_name="Rome",
        latitude=2.0,
        longitude=2.0,
        searched_at=datetime.now(timezone.utc),
    )
    expected_history_list = [mock_log_1, mock_log_2]

    mock_execute_result.scalars = MagicMock()
    mock_execute_result.scalars.return_value.all = MagicMock(
        return_value=expected_history_list
    )
    mock_session.execute = AsyncMock(return_value=mock_execute_result)

    limit = 10
    returned_history = await get_my_search_history(
        mock_session, user_session_id=user_session_id_to_test, limit=limit
    )

    mock_session.execute.assert_called_once()

    assert returned_history == expected_history_list
    mock_execute_result.scalars.assert_called_once()
    mock_execute_result.scalars.return_value.all.assert_called_once()


@pytest.mark.asyncio
async def test_get_my_search_history_empty_result():
    mock_session = MagicMock(spec=AsyncSession)
    mock_execute_result = MagicMock()

    expected_history_list = []

    mock_execute_result.scalars = MagicMock()
    mock_execute_result.scalars.return_value.all = MagicMock(
        return_value=expected_history_list
    )
    mock_session.execute = AsyncMock(return_value=mock_execute_result)

    user_session_id_to_test = str(uuid4())
    limit = 10
    returned_history = await get_my_search_history(
        mock_session, user_session_id=user_session_id_to_test, limit=limit
    )

    mock_session.execute.assert_called_once()
    assert returned_history == expected_history_list
