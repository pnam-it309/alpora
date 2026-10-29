"""Networking and radio subsystem adapter using SafeRunner."""
from __future__ import annotations

from typing import Any
from .base import SafeRunner


class NetworkAdapter:
    """Encapsulates interaction with NetworkManager, rfkill, and bluetoothctl."""

    @classmethod
    def is_nm_available(cls) -> bool:
        return SafeRunner.is_available("nmcli")

    @classmethod
    def is_rfkill_available(cls) -> bool:
        return SafeRunner.is_available("rfkill")

    @classmethod
    def is_bluetooth_available(cls) -> bool:
        return SafeRunner.is_available("bluetoothctl")

    @classmethod
    def get_radio_status(cls) -> dict[str, bool]:
        """Check Wi-Fi and WWAN radio status via nmcli."""
        if not cls.is_nm_available():
            return {"wifi": False, "wwan": False}
        res = SafeRunner.run(["nmcli", "-t", "-f", "WIFI,WWAN", "radio"], timeout=3.0)
        if res.returncode == 0:
            parts = res.stdout.strip().split(":")
            if len(parts) == 2:
                return {
                    "wifi": parts[0].strip() == "enabled",
                    "wwan": parts[1].strip() == "enabled",
                }
        return {"wifi": False, "wwan": False}

    @classmethod
    def set_wifi_enabled(cls, enabled: bool) -> bool:
        """Enable or disable Wi-Fi radio via nmcli."""
        arg = "on" if enabled else "off"
        res = SafeRunner.run(["nmcli", "radio", "wifi", arg], timeout=4.0)
        return res.returncode == 0

    @classmethod
    def block_rfkill(cls, identifier_or_all: str, block: bool) -> bool:
        """Block or unblock wireless devices via rfkill."""
        action = "block" if block else "unblock"
        res = SafeRunner.run(["rfkill", action, str(identifier_or_all)], timeout=4.0)
        return res.returncode == 0
