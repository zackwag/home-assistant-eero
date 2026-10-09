"""Fixtures for Eero integration tests."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest


@pytest.fixture
def mock_api():
    """Return a mocked EeroAPI."""
    with patch("custom_components.eero.api.EeroAPI") as mock:
        api = mock.return_value
        api.login = AsyncMock()
        api.login_verify = AsyncMock()
        api.login_refresh = AsyncMock()
        api.update = AsyncMock()
        yield api
