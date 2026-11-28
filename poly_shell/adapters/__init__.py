"""System and hardware adapters for ALPORA."""
import os
from .base import SafeRunner
from .compositor_base import BaseCompositorAdapter
from .hyprland import HyprlandAdapter
from .generic_wlroots import GenericWlrootsAdapter
from .audio import AudioAdapter
from .network import NetworkAdapter


def get_compositor_adapter() -> type[BaseCompositorAdapter]:
    """Resolve active compositor adapter based on environment and available tools."""
    current_desktop = os.environ.get("XDG_CURRENT_DESKTOP", "").lower()
    if "hyprland" in current_desktop or HyprlandAdapter.is_available():
        return HyprlandAdapter
    if GenericWlrootsAdapter.is_available():
        return GenericWlrootsAdapter
    return HyprlandAdapter


__all__ = [
    "SafeRunner",
    "BaseCompositorAdapter",
    "HyprlandAdapter",
    "GenericWlrootsAdapter",
    "get_compositor_adapter",
    "AudioAdapter",
    "NetworkAdapter",
]
