"""Poly Shell: a workspace-oriented Hyprland shell, currently a foundation preview."""
from .watchdog import CrashReporter

__version__ = "0.1.0-dev"

# Automatically install non-invasive telemetry and crash reporting
CrashReporter.install()
