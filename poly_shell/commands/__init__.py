"""CLI subcommand handlers for ALPORA Command Pattern."""
from .screen_cmd import handle_screen
from .wellbeing_cmd import handle_wellbeing
from .doctor_cmd import handle_doctor, handle_preflight

__all__ = ["handle_screen", "handle_wellbeing", "handle_doctor", "handle_preflight"]
