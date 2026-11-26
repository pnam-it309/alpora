# `poly_shell/services/` — Stateful Domain Services

This package contains **object-oriented domain services** (inheriting from `BaseService` in `poly_shell/core/service.py`) orchestrated by `PolyShellDaemon` (`poly_shell/core/daemon.py`).

## Responsibilities
Each service encapsulates a domain model, returns typed DTOs from `poly_shell/contracts/hardware.py`, implements `health_check()`, and registers RPC handlers on the Unix Domain Socket IPC server (`ipc.sock`):
- **`audio_service.py` / `network_service.py` / `power_service.py`**: Real-time audio, network, and power state for IPC clients.
- **`metrics_service.py` / `developer_metrics.py` / `memory_service.py`**: CPU/GPU/RAM/zRAM telemetry, PSI thrashing detection, and Memory Shield optimization.
- **`security_service.py` / `privacy_service.py` / `storage_service.py` / `snapshot_service.py`**: Kernel hardening audits, app sandbox permissions, CleanGuard cache reclamation, and Btrfs snapshots.
- **`game_mode.py` / `phone_service.py` / `dev_toolbox.py` / `file_inspector.py`**: Game Mode tweaks, KDE Connect phone ecosystem, isolated developer CLI toolchain, and file checksum inspector.
- **`clipboard_service.py` / `organizer.py` / `shortcuts.py` / `task_manager.py` / `wellbeing.py`**: Persistent user productivity and workspace services.

## Architectural Boundary (`services/` vs `system/`)
- Use `poly_shell/services/` for **daemon-hosted services and typed DTO domain logic**.
- Use `poly_shell/system/` for **low-level OS bootstrap, dotfiles/config generators, and one-shot shell adapters**.
