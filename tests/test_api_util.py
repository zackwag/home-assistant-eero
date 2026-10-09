"""Tests for Eero API utility functions."""

from __future__ import annotations

from custom_components.eero.api.util import (
    backup_access_point_ok,
    generate_qr_code,
    premium_ok,
)


def test_generate_qr_code_with_password():
    """Test QR code generation with password."""
    result = generate_qr_code(ssid="MyNetwork", password="secret123")
    assert result is not None
    assert isinstance(result, bytes)
    assert len(result) > 0


def test_generate_qr_code_without_password():
    """Test QR code generation without password."""
    result = generate_qr_code(ssid="OpenNetwork", password=None)
    assert result is not None
    assert isinstance(result, bytes)


def test_generate_qr_code_none_ssid():
    """Test QR code generation returns None for None ssid."""
    result = generate_qr_code(ssid=None, password="secret")
    assert result is None


def test_premium_ok():
    """Test premium_ok helper."""
    assert premium_ok(capable=True, status="active")
    assert premium_ok(capable=True, status="trialing")
    assert not premium_ok(capable=True, status="expired")
    assert not premium_ok(capable=False, status="active")
    assert not premium_ok(capable=None, status="active")


def test_backup_access_point_ok():
    """Test backup_access_point_ok helper."""
    assert backup_access_point_ok(capable=True, requirements={"req1": True, "req2": True})
    assert not backup_access_point_ok(capable=True, requirements={"req1": True, "req2": False})
    assert not backup_access_point_ok(capable=False, requirements={"req1": True})
