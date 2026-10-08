"""Eero API."""

from __future__ import annotations

import io

import pyqrcode

from .const import STATE_ACTIVE, STATE_TRIALING


def generate_qr_code(ssid: str, password: str | None) -> bytes | None:
    """Generate QR code."""
    if ssid is None:
        return None
    if password:
        wifi_code = f"WIFI:S:{ssid};H:false;T:WPA/WPA2;P:{password};;"
    else:
        wifi_code = f"WIFI:S:{ssid};H:false;T:nopass;;"
    qr_stream = io.BytesIO()
    qr_code = pyqrcode.create(wifi_code)
    qr_code.png(qr_stream, scale=5, module_color="#000", background="#FFF")
    return qr_stream.getvalue()


def backup_access_point_ok(capable: bool | None, requirements: dict | None) -> bool:
    """Backup access point OK."""
    return capable and all(bool(value) for value in requirements.values())


def premium_ok(capable: bool | None, status: str | None) -> bool:
    """Premium OK."""
    return bool(capable) and status in (STATE_ACTIVE, STATE_TRIALING)
