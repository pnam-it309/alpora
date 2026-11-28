"""Game Mode service for CPU governor tuning, Hyprland load reduction, and gaming optimizations."""
from __future__ import annotations

import glob
import json
import logging
import os
from pathlib import Path
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional

from ..adapters.base import SafeRunner
from ..contracts.hardware import GameModeDTO
from ..core.service import BaseService
from ..core.state import Paths

logger = logging.getLogger(__name__)

HOYOVERSE_PRESETS: Dict[str, Dict[str, Any]] = {
    "zzz": {
        "title": "Zenless Zone Zero (ZZZ)",
        "description": "Ultra-responsive combat profile with asynchronous DXVK pipeline caching and low-latency audio.",
        "aur_launcher": "aagl-gtk-bin (An Anime Game Launcher)",
        "env_vars": {
            "WINEESYNC": "1",
            "WINEFSYNC": "1",
            "DXVK_ASYNC": "1",
            "DXVK_STATE_CACHE": "1",
            "STAGING_SHARED_MEMORY": "1",
            "PULSE_LATENCY_MSEC": "30",
            "MESA_VK_WSI_PRESENT_MODE": "mailbox",
            "__GL_SHADER_DISK_CACHE": "1",
            "__GL_SHADER_DISK_CACHE_SKIP_CLEANUP": "1",
        },
        "recommendations": [
            "Install 'aagl-gtk-bin' or 'anime-game-launcher' from AUR for automated patch management.",
            "Use Proton-GE or Wine-GE for direct DX11/DX12 translation.",
            "Set in-game display mode to 'Borderless Windowed' for optimal Hyprland Wayland tearing-free sync.",
        ],
    },
    "honkai": {
        "title": "Honkai: Star Rail (HSR)",
        "description": "Stable frame-rate profile with shader pre-caching and high-efficiency CPU scheduling.",
        "aur_launcher": "aagl-gtk-bin (The Honkai Star Rail Launcher)",
        "env_vars": {
            "WINEESYNC": "1",
            "WINEFSYNC": "1",
            "DXVK_ASYNC": "1",
            "DXVK_STATE_CACHE": "1",
            "STAGING_SHARED_MEMORY": "1",
            "PULSE_LATENCY_MSEC": "40",
            "MESA_VK_WSI_PRESENT_MODE": "mailbox",
            "DXVK_FRAME_RATE": "60",
        },
        "recommendations": [
            "Set FPS Limit to 60 or 120 according to your monitor refresh rate.",
            "Enable DXVK Async to eliminate first-load combat stuttering.",
            "Use GameMode to ensure CPU scheduler prioritizes the Star Rail main render thread.",
        ],
    },
    "genshin": {
        "title": "Genshin Impact",
        "description": "Open-world exploration profile with texture streaming optimizations.",
        "aur_launcher": "aagl-gtk-bin (An Anime Game Launcher)",
        "env_vars": {
            "WINEESYNC": "1",
            "WINEFSYNC": "1",
            "DXVK_ASYNC": "1",
            "DXVK_STATE_CACHE": "1",
            "MESA_VK_WSI_PRESENT_MODE": "mailbox",
        },
        "recommendations": [
            "Borderless Fullscreen recommended under Hyprland.",
            "Install 'gamemode' package for kernel-level CPU core pinning.",
        ],
    },
}
HOYOVERSE_PRESETS["starrail"] = HOYOVERSE_PRESETS["honkai"]

KNOWN_GAME_PATTERNS = [
    "wine", "wineserver", "gamescope", "steam", "lutris", "heroic",
    "aagl", "starrail", "genshin", "zenless", "proton",
]


class GameModeService(BaseService):
    """Orchestrates gaming performance boosts and suspends compositor overhead."""

    def __init__(self, paths: Optional[Paths] = None):
        super().__init__("gamemode")
        self.paths = paths or Paths.current()

    def health_check(self) -> bool:
        return (
            SafeRunner.is_available("powerprofilesctl")
            or SafeRunner.is_available("cpupower")
            or SafeRunner.is_available("gamemoded")
            or SafeRunner.is_available("hyprctl")
        )

    def _marker_path(self) -> Path:
        return self.paths.state / "gamemode.active"

    def _get_current_governor(self) -> str:
        """Query active CPU governor via powerprofilesctl, cpupower, or sysfs."""
        if SafeRunner.is_available("powerprofilesctl"):
            res = SafeRunner.run(["powerprofilesctl", "get"], timeout=2.0)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        sys_gov = Path("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor")
        if sys_gov.exists():
            try:
                return sys_gov.read_text(encoding="utf-8").strip()
            except OSError:
                pass
        return "balanced"

    def _apply_cpu_governor(self, governor: str) -> bool:
        """Apply target CPU governor across available interfaces."""
        success = False
        if SafeRunner.is_available("powerprofilesctl"):
            target_profile = "performance" if governor == "performance" else "balanced"
            res = SafeRunner.run(["powerprofilesctl", "set", target_profile], timeout=2.0)
            if res.returncode == 0:
                success = True

        if SafeRunner.is_available("cpupower"):
            res = SafeRunner.run(["cpupower", "frequency-set", "-g", governor], timeout=2.0)
            if res.returncode == 0:
                success = True

        # Sysfs fallback if writable
        for gov_path in glob.glob("/sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"):
            try:
                Path(gov_path).write_text(governor, encoding="utf-8")
                success = True
            except OSError:
                break
        return success

    def _find_and_renice_games(self, game_name: Optional[str] = None, priority: int = -5) -> List[int]:
        """Elevate process priority (renice) for gaming processes."""
        reniced_pids: List[int] = []
        patterns = list(KNOWN_GAME_PATTERNS)
        if game_name:
            patterns.append(game_name.lower().replace(" ", "").replace(":", ""))

        proc_dir = Path("/proc")
        if not proc_dir.exists():
            return reniced_pids

        for pid_entry in proc_dir.iterdir():
            if not pid_entry.is_dir() or not pid_entry.name.isdigit():
                continue
            pid = int(pid_entry.name)
            try:
                comm_file = pid_entry / "comm"
                if not comm_file.exists():
                    continue
                comm = comm_file.read_text(encoding="utf-8", errors="replace").strip().lower()
                if any(p in comm for p in patterns):
                    try:
                        os.setpriority(os.PRIO_PROCESS, pid, priority)
                        reniced_pids.append(pid)
                    except (PermissionError, OSError):
                        # Try via renice command if direct setpriority fails
                        res = SafeRunner.run(["renice", "-n", str(priority), "-p", str(pid)], timeout=1.0)
                        if res.returncode == 0:
                            reniced_pids.append(pid)
            except OSError:
                continue

        return reniced_pids

    def get_state(self) -> GameModeDTO:
        marker = self._marker_path()
        is_active = marker.exists()
        active_game: Optional[str] = None
        dnd_active = False

        if is_active:
            try:
                data = json.loads(marker.read_text(encoding="utf-8"))
                active_game = data.get("game")
                dnd_active = bool(data.get("dnd_suppressed"))
            except Exception:
                active_game = None

        governor = self._get_current_governor()

        optimizations: List[str] = []
        if is_active:
            optimizations.append("hyprland_animations_disabled")
            optimizations.append("hyprland_blur_disabled")
            optimizations.append("hyprland_drop_shadow_disabled")
            if governor == "performance":
                optimizations.append("cpu_governor_performance")
            if dnd_active:
                optimizations.append("notifications_silenced_dnd")
            if SafeRunner.is_available("gamemoded"):
                optimizations.append("feral_gamemode_active")

        return GameModeDTO(
            enabled=is_active,
            active_game=active_game,
            cpu_governor=governor,
            animations_disabled=is_active,
            blur_disabled=is_active,
            gamemode_available=SafeRunner.is_available("gamemoded"),
            optimizations=optimizations,
        )

    def _get_hyprland_bool_option(self, option_name: str) -> Optional[int]:
        """Query current Hyprland boolean/int option via hyprctl."""
        if not SafeRunner.is_available("hyprctl"):
            return None
        res = SafeRunner.run(["hyprctl", "getoption", option_name, "-j"], timeout=2.0)
        if res.returncode == 0 and res.stdout.strip():
            try:
                data = json.loads(res.stdout)
                if "int" in data:
                    return int(data["int"])
                if "bool" in data:
                    return 1 if data["bool"] else 0
            except Exception:
                pass
        return None

    def enable(self, game_name: Optional[str] = None, silence_notifications: bool = True) -> bool:
        """Activates Game Mode, disables compositor eye-candy, tunes CPU, and renices games."""
        marker = self._marker_path()
        self.paths.state.mkdir(parents=True, exist_ok=True)

        prev_gov = self._get_current_governor()
        prev_dnd = False

        # Query and preserve previous Hyprland compositor options (animations, blur, shadow, vfr)
        prev_animations = self._get_hyprland_bool_option("animations:enabled")
        prev_blur = self._get_hyprland_bool_option("decoration:blur:enabled")
        prev_shadow = self._get_hyprland_bool_option("decoration:shadow:enabled")
        if prev_shadow is None:
            prev_shadow = self._get_hyprland_bool_option("decoration:drop_shadow")
        prev_vfr = self._get_hyprland_bool_option("misc:vfr")

        # Check existing notification / DND state
        if SafeRunner.is_available("makoctl"):
            mode_res = SafeRunner.run(["makoctl", "mode"], timeout=2.0)
            if mode_res.returncode == 0 and "do-not-disturb" in mode_res.stdout:
                prev_dnd = True

        # 1. Reduce compositor GPU/CPU overhead in Hyprland
        if SafeRunner.is_available("hyprctl"):
            SafeRunner.run(["hyprctl", "keyword", "animations:enabled", "0"], timeout=2.0)
            SafeRunner.run(["hyprctl", "keyword", "decoration:blur:enabled", "0"], timeout=2.0)
            SafeRunner.run(["hyprctl", "keyword", "decoration:drop_shadow", "0"], timeout=2.0)
            SafeRunner.run(["hyprctl", "keyword", "decoration:shadow:enabled", "0"], timeout=2.0)
            SafeRunner.run(["hyprctl", "keyword", "misc:vfr", "0"], timeout=2.0)

        # 2. Elevate CPU governor to maximum performance
        self._apply_cpu_governor("performance")

        # 3. Renice running game processes
        reniced = self._find_and_renice_games(game_name, priority=-5)

        # 4. Silence notifications if requested
        dnd_suppressed = False
        if silence_notifications and not prev_dnd and SafeRunner.is_available("makoctl"):
            SafeRunner.run(["makoctl", "mode", "-a", "do-not-disturb"], timeout=2.0)
            dnd_suppressed = True

        # 5. Request Feral GameMode daemon if available
        if SafeRunner.is_available("gamemoded"):
            SafeRunner.run(["gamemoded", "-r"], timeout=2.0)

        payload = {
            "game": game_name or "Generic Game",
            "started_at": time.time(),
            "previous_governor": prev_gov,
            "previous_dnd": prev_dnd,
            "dnd_suppressed": dnd_suppressed,
            "reniced_pids": reniced,
            "prev_animations": prev_animations,
            "prev_blur": prev_blur,
            "prev_shadow": prev_shadow,
            "prev_vfr": prev_vfr,
        }
        marker.write_text(json.dumps(payload), encoding="utf-8")

        logger.info("ALPORA Game Mode ENABLED for: %s (Reniced: %d)", payload["game"], len(reniced))
        return True

    def disable(self) -> bool:
        """Deactivates Game Mode and smoothly restores compositor animations, CPU governor, and DND."""
        marker = self._marker_path()
        prev_gov = "balanced"
        dnd_suppressed = False
        reniced_pids: List[int] = []
        saved: Dict[str, Any] = {}

        if marker.exists():
            try:
                saved = json.loads(marker.read_text(encoding="utf-8"))
                prev_gov = saved.get("previous_governor", "balanced")
                dnd_suppressed = bool(saved.get("dnd_suppressed", False))
                reniced_pids = saved.get("reniced_pids", [])
                marker.unlink()
            except Exception:
                pass

        # 1. Restore Hyprland animations, blur, shadows, and vfr to previous states
        if SafeRunner.is_available("hyprctl"):
            anim_val = "1" if saved.get("prev_animations", 1) != 0 else "0"
            blur_val = "1" if saved.get("prev_blur", 1) != 0 else "0"
            shadow_val = "1" if saved.get("prev_shadow", 1) != 0 else "0"
            vfr_val = "1" if saved.get("prev_vfr", 1) != 0 else "0"

            SafeRunner.run(["hyprctl", "keyword", "animations:enabled", anim_val], timeout=2.0)
            SafeRunner.run(["hyprctl", "keyword", "decoration:blur:enabled", blur_val], timeout=2.0)
            SafeRunner.run(["hyprctl", "keyword", "decoration:drop_shadow", shadow_val], timeout=2.0)
            SafeRunner.run(["hyprctl", "keyword", "decoration:shadow:enabled", shadow_val], timeout=2.0)
            SafeRunner.run(["hyprctl", "keyword", "misc:vfr", vfr_val], timeout=2.0)

        # 2. Revert CPU governor to previous state
        self._apply_cpu_governor(prev_gov)

        # 3. Restore DND / notifications if suppressed
        if dnd_suppressed and SafeRunner.is_available("makoctl"):
            SafeRunner.run(["makoctl", "mode", "-r", "do-not-disturb"], timeout=2.0)

        # 4. Restore reniced process priorities back to 0
        for pid in reniced_pids:
            try:
                os.setpriority(os.PRIO_PROCESS, pid, 0)
            except OSError:
                SafeRunner.run(["renice", "-n", "0", "-p", str(pid)], timeout=1.0)

        logger.info("ALPORA Game Mode DISABLED. Restored default compositor, CPU, and notifications.")
        return True

    def toggle(self, game_name: Optional[str] = None) -> bool:
        """Toggles Game Mode on or off."""
        if self._marker_path().exists():
            self.disable()
            return False
        else:
            self.enable(game_name)
            return True

    @staticmethod
    def get_hoyoverse_preset(name: str) -> Dict[str, Any]:
        """Returns optimized environment variables and recommendations for a Hoyoverse title."""
        key = name.lower().strip()
        if key in ("zzz", "zenless", "zenlesszonezero", "zenless-zone-zero"):
            return HOYOVERSE_PRESETS["zzz"]
        elif key in ("honkai", "starrail", "hsr", "honkai-star-rail", "star-rail"):
            return HOYOVERSE_PRESETS["honkai"]
        elif key in ("genshin", "gi", "genshin-impact"):
            return HOYOVERSE_PRESETS["genshin"]
        return HOYOVERSE_PRESETS["zzz"]

    def launch_game(self, command_args: List[str], game_name: Optional[str] = None) -> int:
        """Launches a game command wrapped with Game Mode lifecycle and Hoyoverse optimizations."""
        preset = self.get_hoyoverse_preset(game_name or (command_args[0] if command_args else "zzz"))
        env = os.environ.copy()
        env.update(preset.get("env_vars", {}))

        self.enable(preset["title"])
        try:
            res = subprocess.run(command_args, env=env, check=False)
            return res.returncode
        finally:
            self.disable()
