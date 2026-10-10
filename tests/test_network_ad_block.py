"""Tests for the read-only network ad block status."""

from __future__ import annotations

import pytest

from custom_components.eero.api.const import STATE_DISABLED, STATE_NETWORK, STATE_PROFILE
from custom_components.eero.api.network import EeroNetwork


def _network(ad_block_settings: dict | None) -> EeroNetwork:
    network = EeroNetwork.__new__(EeroNetwork)
    network.data = {} if ad_block_settings is None else {"premium_dns": {"ad_block_settings": ad_block_settings}}
    return network


@pytest.mark.parametrize(
    ("settings", "expected"),
    [
        ({"enabled": True, "profiles": []}, STATE_NETWORK),
        ({"enabled": True, "profiles": ["/2.2/networks/1/profiles/2"]}, STATE_PROFILE),
        ({"enabled": False, "profiles": []}, STATE_DISABLED),
        (None, STATE_DISABLED),
    ],
)
def test_ad_block_status(settings, expected):
    """Network-wide, per-profile, and off are distinguished from the envelope alone."""
    assert _network(settings).ad_block_status == expected
