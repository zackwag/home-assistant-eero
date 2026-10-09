"""Tests for Eero API client model."""

from __future__ import annotations

from unittest.mock import MagicMock

from custom_components.eero.api.client import EeroClient


def _make_client(data: dict) -> EeroClient:
    """Create a test client with given data."""
    api = MagicMock()
    network = MagicMock()
    network.data = {}
    return EeroClient(api, network, data)


def test_channel_width_rx_none_connectivity():
    """Test channel_width_rx when connectivity is None."""
    client = _make_client({"connectivity": None})
    assert client.channel_width_rx is None


def test_channel_width_rx_missing_connectivity():
    """Test channel_width_rx when connectivity is missing."""
    client = _make_client({})
    assert client.channel_width_rx is None


def test_channel_width_tx_none_connectivity():
    """Test channel_width_tx when connectivity is None."""
    client = _make_client({"connectivity": None})
    assert client.channel_width_tx is None


def test_interface_frequency_none():
    """Test interface_frequency when interface is None."""
    client = _make_client({"interface": None})
    assert client.interface_frequency == (None, None)


def test_interface_frequency_missing():
    """Test interface_frequency when interface is missing."""
    client = _make_client({})
    assert client.interface_frequency == (None, None)


def test_source_location_none():
    """Test source_location when source is None."""
    client = _make_client({"source": None})
    assert client.source_location is None


def test_source_location_missing():
    """Test source_location when source is missing."""
    client = _make_client({})
    assert client.source_location is None


def test_signal_none_connectivity():
    """Test signal when connectivity is None."""
    client = _make_client({"connectivity": None})
    assert client.signal == (None, None)


def test_signal_missing_connectivity():
    """Test signal when connectivity is missing."""
    client = _make_client({})
    assert client.signal == (None, None)


def test_data_usage_day_no_activity():
    """Test data_usage_day returns None tuple when no activity data."""
    client = _make_client({"url": "/test"})
    assert client.data_usage_day == (None, None)


def test_connected_returns_value():
    """Test connected property returns the API value."""
    client = _make_client({"connected": True})
    assert client.connected is True

    client = _make_client({"connected": False})
    assert client.connected is False


def test_name_priority():
    """Test name returns nickname > hostname > mac."""
    assert _make_client({"nickname": "My Phone", "hostname": "phone", "mac": "AA:BB"}).name == "My Phone"
    assert _make_client({"nickname": None, "hostname": "phone", "mac": "AA:BB"}).name == "phone"
    assert _make_client({"nickname": None, "hostname": None, "mac": "AA:BB"}).name == "AA:BB"
