"""Tests for EeroAPI.call URL handling."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

from custom_components.eero.api import EeroAPI
from custom_components.eero.api.const import METHOD_GET, URL_ACCOUNT


async def test_call_sends_fully_qualified_url():
    """Versioned relative URLs must not be re-prefixed with the library's versioned base."""
    api = EeroAPI(session=MagicMock(), user_token="token")
    api._lib.auth.get = AsyncMock(return_value={"data": {"ok": True}})

    assert await api.call(method=METHOD_GET, url=URL_ACCOUNT) == {"ok": True}
    api._lib.auth.get.assert_awaited_once_with("https://api-user.e2ro.com/2.2/account", auth_token="token")


async def test_call_leaves_absolute_url_unchanged():
    """Absolute URLs pass through as-is."""
    api = EeroAPI(session=MagicMock(), user_token="token")
    api._lib.auth.get = AsyncMock(return_value={"data": {}})

    await api.call(method=METHOD_GET, url="https://example.com/x")
    api._lib.auth.get.assert_awaited_once_with("https://example.com/x", auth_token="token")
