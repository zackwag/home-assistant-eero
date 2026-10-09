"""Tests for Eero sensor helpers."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eero.sensor import _sum_data_usage


def test_sum_data_usage_normal():
    """Test _sum_data_usage with valid values."""
    resource = MagicMock()
    resource.data_usage_day = (100, 200)
    assert _sum_data_usage(resource, "data_usage_day") == 300


def test_sum_data_usage_none_download():
    """Test _sum_data_usage returns None when download is None."""
    resource = MagicMock()
    resource.data_usage_day = (None, 200)
    assert _sum_data_usage(resource, "data_usage_day") is None


def test_sum_data_usage_none_upload():
    """Test _sum_data_usage returns None when upload is None."""
    resource = MagicMock()
    resource.data_usage_day = (100, None)
    assert _sum_data_usage(resource, "data_usage_day") is None


def test_sum_data_usage_both_none():
    """Test _sum_data_usage returns None when both are None."""
    resource = MagicMock()
    resource.data_usage_day = (None, None)
    assert _sum_data_usage(resource, "data_usage_day") is None


def test_sum_data_usage_zero():
    """Test _sum_data_usage with zero values."""
    resource = MagicMock()
    resource.data_usage_day = (0, 0)
    assert _sum_data_usage(resource, "data_usage_day") == 0
