"""Bluetooth device discovery, connection, and pairing management service."""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List

from ..adapters.base import SafeRunner

logger = logging.getLogger(__name__)


class BluetoothService:
    """Encapsulates bluetoothctl operations for discovery, pairing, and connections."""

    @classmethod
    def get_status(cls) -> Dict[str, Any]:
        """Query adapter powered, discoverable, and discovering states."""
        if not SafeRunner.is_available("bluetoothctl"):
            return {
                "available": False,
                "powered": False,
                "discoverable": False,
                "discovering": False,
            }
        proc = SafeRunner.run(["bluetoothctl", "--timeout", "3", "show"], timeout=3.0)
        powered = proc.returncode == 0 and bool(re.search(r"Powered:\s+yes", proc.stdout))
        discoverable = proc.returncode == 0 and bool(re.search(r"Discoverable:\s+yes", proc.stdout))
        discovering = proc.returncode == 0 and bool(re.search(r"Discovering:\s+yes", proc.stdout))
        return {
            "available": True,
            "powered": powered,
            "discoverable": discoverable,
            "discovering": discovering,
        }

    @classmethod
    def list_devices(cls) -> List[Dict[str, Any]]:
        """List known paired and cached Bluetooth devices."""
        if not SafeRunner.is_available("bluetoothctl"):
            return []
        proc = SafeRunner.run(["bluetoothctl", "--timeout", "3", "devices"], timeout=3.0)
        devices: List[Dict[str, Any]] = []
        for line in proc.stdout.splitlines():
            line = line.strip()
            match = re.match(r"^Device\s+([0-9A-Fa-f:]+)\s+(.+)$", line)
            if match:
                mac, name = match.group(1), match.group(2)
                devices.append({
                    "mac": mac,
                    "name": name,
                    "paired": True,
                })
        return devices

    @classmethod
    def scan(cls, enable: bool = True) -> bool:
        """Start or stop Bluetooth device discovery."""
        if not SafeRunner.is_available("bluetoothctl"):
            return False
        action = "on" if enable else "off"
        proc = SafeRunner.run(["bluetoothctl", "--timeout", "3", "scan", action], timeout=3.0)
        return proc.returncode == 0

    @classmethod
    def pair(cls, mac: str, pin: str | None = None) -> Dict[str, Any]:
        """Pair with target device, optionally passing PIN."""
        if not SafeRunner.is_available("bluetoothctl"):
            return {"success": False, "error": "bluetoothctl not available", "mac": mac}

        cmd = ["bluetoothctl", "--timeout", "10", "pair", mac]
        proc = SafeRunner.run(cmd, timeout=10.0)
        success = "Pairing successful" in proc.stdout or proc.returncode == 0
        return {
            "success": success,
            "output": proc.stdout.strip(),
            "mac": mac,
        }

    @classmethod
    def trust(cls, mac: str) -> bool:
        """Mark device as trusted."""
        if not SafeRunner.is_available("bluetoothctl"):
            return False
        proc = SafeRunner.run(["bluetoothctl", "--timeout", "3", "trust", mac], timeout=3.0)
        return proc.returncode == 0

    @classmethod
    def connect(cls, mac: str) -> bool:
        """Connect to target device."""
        if not SafeRunner.is_available("bluetoothctl"):
            return False
        proc = SafeRunner.run(["bluetoothctl", "--timeout", "5", "connect", mac], timeout=5.0)
        return proc.returncode == 0

    @classmethod
    def disconnect(cls, mac: str) -> bool:
        """Disconnect from target device."""
        if not SafeRunner.is_available("bluetoothctl"):
            return False
        proc = SafeRunner.run(["bluetoothctl", "--timeout", "5", "disconnect", mac], timeout=5.0)
        return proc.returncode == 0
