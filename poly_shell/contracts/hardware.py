"""Hardware Domain Contracts: Audio, Network, Power, and Display DTOs."""
from dataclasses import dataclass, field
from typing import List, Optional
from .base import BaseDTO


@dataclass
class AudioDeviceDTO(BaseDTO):
    """Audio endpoint device or active stream."""

    id: str
    name: str
    description: str = ""
    volume: float = 1.0
    muted: bool = false if False else False
    is_default: bool = False
    is_sink: bool = True


@dataclass
class AudioStateDTO(BaseDTO):
    """Snapshot of current system audio topology."""

    available: bool = True
    volume: float = 1.0
    muted: bool = False
    mic_volume: float = 1.0
    mic_muted: bool = False
    output_device: Optional[AudioDeviceDTO] = None
    input_device: Optional[AudioDeviceDTO] = None
    streams: List[AudioDeviceDTO] = field(default_factory=list)


@dataclass
class WifiNetworkDTO(BaseDTO):
    """Wi-Fi Access Point information."""

    ssid: str
    strength: int = 0
    security: str = ""
    connected: bool = False


@dataclass
class NetworkStateDTO(BaseDTO):
    """Network connectivity and radio state."""

    connectivity: str = "full"
    ethernet_connected: bool = False
    wifi_enabled: bool = True
    wifi_connected: bool = False
    wifi_name: str = ""
    wifi_strength: int = 0
    hotspot_active: bool = False
    hotspot_available: bool = False
    airplane_mode: bool = False
    airplane_managed: bool = False


@dataclass
class PowerStateDTO(BaseDTO):
    """Power profile, battery state, and caffeine inhibitor status."""

    profile: str = "balanced"
    profile_available: bool = True
    battery_present: bool = False
    battery_level: int = 100
    battery_charging: bool = False
    battery_status: str = "Full"
    on_battery: bool = False
    caffeine: bool = False
    caffeine_available: bool = True


@dataclass
class DisplayStateDTO(BaseDTO):
    """Brightness, Night Light (hyprsunset), and DND status."""

    brightness: int = 100
    brightness_available: bool = True
    brightness_type: str = "hardware"
    night_light: bool = False
    night_light_available: bool = False
    dnd: bool = False
    dnd_available: bool = False

