"""CLI subcommand handlers for ALPORA Command Pattern."""
from .screen_cmd import handle_screen
from .wellbeing_cmd import handle_wellbeing
from .doctor_cmd import handle_doctor, handle_preflight
from .exe_cmd import handle_exe

__all__ = ["handle_screen", "handle_wellbeing", "handle_doctor", "handle_preflight", "handle_exe"]

