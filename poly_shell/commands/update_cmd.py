"""CLI command handler and TrueColor TUI Update Center for ALPORA OS."""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from typing import Any, Dict, List, Optional, Tuple

from ..core.state import Paths, ROOT
from ..services.update_service import UpdateService
from ..system.fetch import card_appearance, cells, clean, fit

_DEFAULT_THEME_LABEL = "Alpine"
_DEFAULT_ALPINE_PALETTE: Dict[str, str] = {
    "background": "#202829",
    "surface": "#303a36",
    "accent": "#b8cba1",
    "secondary": "#f1b791",
    "cool": "#a4c5c5",
    "text": "#edf0e5",
    "muted": "#b6c0b5",
    "border": "#59655c",
}
_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
_APPLY_STEPS: Tuple[Tuple[str, str], ...] = (
    ("Kiểm tra kho lưu trữ & máy chủ phát hành", "Checking release channel"),
    ("Tạo bản sao lưu cấu hình nguyên tử", "Creating atomic backup snapshot"),
    ("Tải & đồng bộ mã nguồn ALPORA OS", "Synchronizing OTA update package"),
    ("Làm mới bộ đệm giao diện & tài nguyên", "Refreshing shell & theme caches"),
    ("Khởi động lại dịch vụ ALPORA Shell", "Restarting poly-shell.service"),
)


def _safe_print(*args: Any, file: Any = None, **kwargs: Any) -> None:
    """Print safely even in environments with restricted encodings."""
    target = file or sys.stdout
    msg = " ".join(str(a) for a in args)
    try:
        print(msg, file=target, **kwargs)
    except UnicodeEncodeError:
        try:
            target.buffer.write((msg + "\n").encode("utf-8", errors="replace"))
        except Exception:
            print(msg.encode("ascii", errors="replace").decode("ascii"), file=target, **kwargs)


def _supports_truecolor(stream: Any = None) -> bool:
    """Return True when stdout/stream is an interactive TTY without NO_COLOR."""
    target = stream or sys.stdout
    if "NO_COLOR" in os.environ or os.environ.get("TERM", "") == "dumb":
        return False
    isatty = getattr(target, "isatty", None)
    return bool(callable(isatty) and isatty())


def _load_theme_appearance() -> Tuple[str, Dict[str, str]]:
    """Fetch active theme label and palette via card_appearance, falling back to Alpine."""
    palette = dict(_DEFAULT_ALPINE_PALETTE)
    try:
        label, loaded = card_appearance(Paths.current())
        if isinstance(loaded, dict):
            for key, value in loaded.items():
                if isinstance(value, str) and _HEX_COLOR_RE.match(value):
                    palette[key] = value
        return (label or _DEFAULT_THEME_LABEL), palette
    except Exception:
        return _DEFAULT_THEME_LABEL, palette


def _wrap_cells(text: str, width: int) -> List[str]:
    """Wrap text into lines fitting within `width` terminal display cells."""
    cleaned = clean(text)
    if width <= 1:
        return [cleaned]
    lines: List[str] = []
    for raw_line in cleaned.splitlines() or [""]:
        if not raw_line:
            lines.append("")
            continue
        current = ""
        for ch in raw_line:
            if cells(current + ch) > width:
                lines.append(current)
                current = ch
            else:
                current += ch
        if current or not lines:
            lines.append(current)
    return lines


def _read_single_key() -> str:
    """Read one keypress in interactive mode, with safe line-input fallback."""
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        saved = termios.tcgetattr(fd)
        try:
            tty.setcbreak(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSANOW, saved)
        return ch
    except Exception:
        try:
            line = sys.stdin.readline()
            return line[:1] if line else "q"
        except Exception:
            return "q"


class UpdateCenterTUI:
    """Renders the ALPORA TrueColor TUI Update Center using the active theme palette."""

    def __init__(
        self,
        theme_label: Optional[str] = None,
        palette: Optional[Dict[str, str]] = None,
        color: Optional[bool] = None,
        inner_width: Optional[int] = None,
    ) -> None:
        if theme_label is None or palette is None:
            loaded_label, loaded_palette = _load_theme_appearance()
            self.theme_label = theme_label or loaded_label
            self.palette = palette or loaded_palette
        else:
            self.theme_label = clean(theme_label) or _DEFAULT_THEME_LABEL
            self.palette = dict(_DEFAULT_ALPINE_PALETTE) | palette

        self.color = _supports_truecolor(sys.stdout) if color is None else bool(color)
        if inner_width is not None:
            self.inner_width = max(56, inner_width)
        elif self.color:
            cols = shutil.get_terminal_size((74, 24)).columns
            self.inner_width = max(56, min(72, cols - 4))
        else:
            self.inner_width = 66

    def _ink(self, role: str, bg: bool = False, stream_color: Optional[bool] = None) -> str:
        use_color = self.color if stream_color is None else stream_color
        if not use_color:
            return ""
        hex_color = self.palette.get(role, role)
        if not isinstance(hex_color, str) or not _HEX_COLOR_RE.match(hex_color):
            hex_color = _DEFAULT_ALPINE_PALETTE["text"]
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        return f"\033[{48 if bg else 38};2;{r};{g};{b}m"

    def _style(self, value: str, role: str = "text", bold: bool = False, stream_color: Optional[bool] = None) -> str:
        use_color = self.color if stream_color is None else stream_color
        if not use_color:
            return value
        prefix = ("\033[1m" if bold else "") + self._ink(role, bg=False, stream_color=use_color)
        return f"{prefix}{value}\033[0m"

    def _top_border(self, stream_color: Optional[bool] = None) -> str:
        return self._style("╭" + "─" * self.inner_width + "╮", "border", stream_color=stream_color)

    def _divider(self, stream_color: Optional[bool] = None) -> str:
        return self._style("├" + "─" * self.inner_width + "┤", "border", stream_color=stream_color)

    def _bottom_border(self, stream_color: Optional[bool] = None) -> str:
        return self._style("╰" + "─" * self.inner_width + "╯", "border", stream_color=stream_color)

    def _row(self, content: str, raw_len: int, stream_color: Optional[bool] = None) -> str:
        pad = max(0, self.inner_width - raw_len)
        edge = self._style("│", "border", stream_color=stream_color)
        return f"{edge}{content}{' ' * pad}{edge}"

    def _kv_row(self, key: str, value: str, value_role: str = "text") -> str:
        key_width = 21
        val_width = self.inner_width - 4 - key_width
        k_txt = fit(key, key_width)
        v_txt = fit(value, val_width)
        body = "  " + self._style(k_txt, "secondary") + self._style(v_txt, value_role) + "  "
        return self._row(body, self.inner_width)

    def _text_row(self, text: str, role: str = "text", bold: bool = False, indent: int = 2, stream_color: Optional[bool] = None) -> str:
        avail = self.inner_width - indent - 2
        fitted = fit(text, avail)
        body = (" " * indent) + self._style(fitted, role, bold=bold, stream_color=stream_color) + "  "
        return self._row(body, self.inner_width, stream_color=stream_color)

    def _header_rows(self, subtitle: str = "Over-The-Air System & Shell Updater") -> List[str]:
        """Build the mountain mark + ALPORA OS / UPDATE CENTER banner."""
        w = self.inner_width - 4
        title = "A L P O R A   O S   /   U P D A T E   C E N T E R"
        rows = [
            self._top_border(),
            self._row(
                "  "
                + self._style(fit("    /\\", 12), "cool", bold=True)
                + self._style(fit(title, w - 12), "accent", bold=True)
                + "  ",
                self.inner_width,
            ),
            self._row(
                "  "
                + self._style(fit("   /  \\/\\", 12), "accent", bold=True)
                + self._style(fit(subtitle, w - 12), "muted")
                + "  ",
                self.inner_width,
            ),
            self._row(
                "  "
                + self._style(fit("  / /\\ \\ \\", 12), "border")
                + self._style(fit(f"Theme: {self.theme_label}", w - 12), "secondary")
                + "  ",
                self.inner_width,
            ),
            self._divider(),
        ]
        return rows

    def _swatches_row(self) -> str:
        roles = ("surface", "border", "cool", "accent", "secondary", "text")
        if self.color:
            blocks = "".join(self._ink(role, bg=True) + "   \033[0m" for role in roles)
            raw_len = 2 + len(roles) * 3
            return self._row("  " + blocks, raw_len)
        label = fit("PALETTE  [■ surface] [■ cool] [■ accent] [■ secondary]", self.inner_width - 4)
        return self._row("  " + label + "  ", self.inner_width)

    @staticmethod
    def progress_bar(percent: int, width: int = 20) -> str:
        """Render a Unicode progress bar like `[████████████░░░░░░░░] 60%`."""
        clamped = max(0, min(100, percent))
        filled = round(width * clamped / 100)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}] {clamped:3d}%"

    def render_check(self, info: Dict[str, Any], show_shortcuts: bool = False) -> str:
        """Render the full ALPORA Update Center overview and changelog panel."""
        current_ver = clean(info.get("current_version", "1.0.0"))
        latest_ver = clean(info.get("latest_version", current_ver))
        has_update = bool(info.get("has_update"))

        lines = self._header_rows()
        lines.append(self._kv_row("Phiên bản hiện tại", current_ver, "text"))
        lines.append(self._kv_row("Phiên bản mới nhất", latest_ver, "accent" if has_update else "cool"))
        lines.append(self._kv_row("Giao diện đang dùng", self.theme_label, "cool"))

        if has_update:
            status_text = "[★] ĐÃ TÌM THẤY BẢN CẬP NHẬT MỚI!"
            lines.append(self._kv_row("Trạng thái", status_text, "secondary"))
            lines.append(self._divider())
            lines.append(self._text_row("Changelog / Nội dung cập nhật", role="accent", bold=True))

            title = clean(info.get("release_title") or "")
            if title:
                lines.append(self._text_row(f"Tiêu đề: {title}", role="text"))
            published = clean(info.get("published_at") or "")
            if published:
                lines.append(self._text_row(f"Ngày phát hành: {published[:10]}", role="muted"))

            notes = (info.get("release_notes") or "").strip()
            if notes:
                note_width = self.inner_width - 6
                wrapped: List[str] = []
                for note_line in notes.splitlines()[:10]:
                    wrapped.extend(_wrap_cells(note_line, note_width))
                for wrapped_line in wrapped[:12]:
                    lines.append(self._text_row(wrapped_line, role="text", indent=4))

            iso_url = clean(info.get("iso_download_url") or "")
            if iso_url:
                lines.append(self._divider())
                lines.append(self._text_row("Link tải Live ISO mới:", role="cool", bold=True))
                for url_line in _wrap_cells(iso_url, self.inner_width - 6)[:3]:
                    lines.append(self._text_row(url_line, role="muted", indent=4))

            lines.append(self._divider())
            for hint_line in _wrap_cells(
                "Hướng dẫn: chạy `poly-shell update apply` hoặc `poly-shell update tui`",
                self.inner_width - 4,
            ):
                lines.append(self._text_row(hint_line, role="secondary"))
        else:
            lines.append(self._kv_row("Trạng thái", "[✓] Đang ở phiên bản mới nhất", "accent"))

        lines.append(self._divider())
        lines.append(self._swatches_row())
        lines.append(self._bottom_border())

        if show_shortcuts:
            shortcut_bar = "[U / Enter] Cập nhật ngay   [C] Kiểm tra lại   [D] Chẩn đoán hệ thống   [Q] Thoát"
            lines.append(self._style("  " + shortcut_bar, "accent", bold=True))

        return "\n".join(lines)

    def render_apply_header(self, branch: str) -> str:
        """Render the top banner for the 5-step OTA apply workflow."""
        lines = self._header_rows(subtitle=f"OTA Apply Pipeline  •  Branch: {clean(branch)}")
        lines.append(self._text_row("Đang khởi chạy tiến trình cập nhật ALPORA OS (5 bước)...", role="cool", bold=True))
        lines.append(self._bottom_border())
        return "\n".join(lines)

    def render_step(self, step_index: int, total_steps: int, title_vi: str, title_en: str) -> str:
        """Render a single step line with its progress bar."""
        pct = int(step_index * 100 / total_steps)
        bar = self.progress_bar(pct)
        tag = f"[{step_index}/{total_steps}]"
        return (
            f"  {self._style(tag, 'secondary', bold=True)} "
            f"{self._style(bar, 'accent', bold=True)}  "
            f"{self._style(title_vi, 'text')} "
            f"{self._style(f'({title_en})', 'muted')}"
        )

    def render_apply_result(self, res: Dict[str, Any]) -> Tuple[str, bool]:
        """Render the final result frame (`[THÀNH CÔNG]` or `[LỖI]`)."""
        success = bool(res.get("success"))
        use_color = self.color if success else _supports_truecolor(sys.stderr)
        lines = [self._top_border(stream_color=use_color)]
        if success:
            msg = clean(res.get("message") or "Cập nhật ALPORA OS thành công!")
            lines.append(self._text_row(f"[THÀNH CÔNG] {msg}", role="accent", bold=True, stream_color=use_color))
            backup_path = clean(res.get("backup_path") or "")
            if backup_path:
                for idx, chunk in enumerate(_wrap_cells(backup_path, self.inner_width - 18)):
                    prefix = "Bản sao lưu: " if idx == 0 else "             "
                    lines.append(self._text_row(prefix + chunk, role="cool", stream_color=use_color))
            lines.append(self._divider(stream_color=use_color))
            lines.append(self._swatches_row())
        else:
            err = clean(res.get("error") or "Cập nhật thất bại.")
            for idx, chunk in enumerate(_wrap_cells(err, self.inner_width - 14)):
                prefix = "[LỖI] " if idx == 0 else "      "
                lines.append(self._text_row(prefix + chunk, role="secondary", bold=(idx == 0), stream_color=use_color))
        lines.append(self._bottom_border(stream_color=use_color))
        return "\n".join(lines), success

    def render_diagnostics(self, service: UpdateService) -> str:
        """Render quick system & OTA diagnostics for the TUI `[D]` shortcut."""
        paths = Paths.current()
        git_exists = (ROOT / ".git").exists()
        service_state = "unknown"
        try:
            proc = subprocess.run(
                ["systemctl", "--user", "is-active", "poly-shell.service"],
                capture_output=True,
                text=True,
                timeout=3,
                check=False,
            )
            service_state = proc.stdout.strip() or f"inactive (rc={proc.returncode})"
        except Exception as exc:
            service_state = f"unavailable ({exc})"

        lines = self._header_rows(subtitle="Chẩn đoán hệ thống & Dịch vụ cập nhật")
        lines.append(self._kv_row("Phiên bản", service.get_current_version(), "text"))
        lines.append(self._kv_row("Kho Git cục bộ", "Sẵn sàng (.git)" if git_exists else "Không tìm thấy .git", "accent" if git_exists else "secondary"))
        lines.append(self._kv_row("poly-shell.service", service_state, "cool"))
        lines.append(self._kv_row("Thư mục cấu hình", str(paths.config), "muted"))
        lines.append(self._kv_row("Thư mục sao lưu", str(paths.state / "backups"), "muted"))
        lines.append(self._divider())
        lines.append(self._swatches_row())
        lines.append(self._bottom_border())
        return "\n".join(lines)


def _wait_if_hold(hold: bool) -> None:
    if hold and sys.stdin.isatty():
        try:
            input("\nNhấn Enter để đóng cửa sổ...")
        except (EOFError, KeyboardInterrupt):
            pass


def _run_apply_flow(service: UpdateService, tui: UpdateCenterTUI, branch: str, hold: bool = False) -> int:
    """Execute the 5-step OTA update flow with progress display and atomic single apply_update call."""
    _safe_print(tui.render_apply_header(branch))

    # Step 1 & 2 before invoking service.apply_update once
    for idx in (1, 2):
        vi, en = _APPLY_STEPS[idx - 1]
        _safe_print(tui.render_step(idx, len(_APPLY_STEPS), vi, en))

    # Step 3: Download & synchronize OTA package via single service.apply_update call
    vi3, en3 = _APPLY_STEPS[2]
    _safe_print(tui.render_step(3, len(_APPLY_STEPS), vi3, en3))
    res = service.apply_update(branch=branch)

    if not res.get("success"):
        err_box, _ = tui.render_apply_result(res)
        _safe_print(err_box, file=sys.stderr)
        _wait_if_hold(hold)
        return 1

    # Step 4: Refresh shell & theme caches
    vi4, en4 = _APPLY_STEPS[3]
    _safe_print(tui.render_step(4, len(_APPLY_STEPS), vi4, en4))

    # Step 5: Restart poly-shell.service only after verified success
    vi5, en5 = _APPLY_STEPS[4]
    _safe_print(tui.render_step(5, len(_APPLY_STEPS), vi5, en5))
    try:
        subprocess.run(["systemctl", "--user", "restart", "poly-shell.service"], check=False)
    except Exception:
        pass

    summary_box, _ = tui.render_apply_result(res)
    _safe_print(summary_box)
    _wait_if_hold(hold)
    return 0


def _run_tui_flow(service: UpdateService, tui: UpdateCenterTUI, args: argparse.Namespace) -> int:
    """Display full Update Center TUI and handle auto-apply or interactive shortcuts."""
    branch = getattr(args, "branch", "main") or "main"
    auto_apply = bool(getattr(args, "auto_apply", False))
    interactive = bool(getattr(sys.stdin, "isatty", lambda: False)()) and not auto_apply

    info = service.check_update(force=True)
    _safe_print(tui.render_check(info, show_shortcuts=interactive))

    if auto_apply:
        return _run_apply_flow(service, tui, branch=branch, hold=bool(getattr(args, "hold", False)))

    if not interactive:
        return 0

    while True:
        key = _read_single_key()
        lower = key.lower()
        if lower in ("u", "\r", "\n"):
            return _run_apply_flow(service, tui, branch=branch, hold=True)
        if lower == "c":
            info = service.check_update(force=True)
            _safe_print("")
            _safe_print(tui.render_check(info, show_shortcuts=True))
        elif lower == "d":
            _safe_print("")
            _safe_print(tui.render_diagnostics(service))
            _safe_print("  [C] Quay lại kiểm tra   [U / Enter] Cập nhật ngay   [Q] Thoát")
        elif lower in ("q", "\x1b", "\x03", "\x04", ""):
            return 0


def handle_update(args: argparse.Namespace) -> int:
    """Dispatch `poly-shell update <subcommand>`."""
    service = UpdateService()
    action = getattr(args, "update_action", None)
    tui = UpdateCenterTUI()

    if action == "check" or (action is None and getattr(args, "json", False)):
        info = service.check_update(force=True)
        if getattr(args, "json", False):
            _safe_print(json.dumps(info, ensure_ascii=False))
            return 0
        _safe_print(tui.render_check(info, show_shortcuts=False))
        return 0

    if action == "apply":
        branch = getattr(args, "branch", "main") or "main"
        hold = bool(getattr(args, "hold", False))
        return _run_apply_flow(service, tui, branch=branch, hold=hold)

    if action == "status":
        ver = service.get_current_version()
        if getattr(args, "json", False):
            _safe_print(json.dumps({"version": ver}, ensure_ascii=False))
        else:
            _safe_print(f"ALPORA OS Version: {ver}")
        return 0

    if action == "tui" or action is None:
        return _run_tui_flow(service, tui, args)

    return 0
