"""RFC 5545 iCalendar (.ics) generator and parser for ALPORA Day Planner."""
from __future__ import annotations

from datetime import datetime, timezone
import re
import uuid
from typing import Any, Dict, List, Tuple

from ..core.state import ConfigError


def unfold_ics(content: str) -> List[str]:
    """Unfold lines split according to RFC 5545 section 3.1 (lines beginning with space/tab)."""
    lines: List[str] = []
    for raw_line in content.splitlines():
        if not raw_line:
            continue
        if (raw_line.startswith(" ") or raw_line.startswith("\t")) and lines:
            lines[-1] += raw_line[1:]
        else:
            lines.append(raw_line)
    return lines


def escape_ics(text: str) -> str:
    """Escape text characters per RFC 5545."""
    return (
        text.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def unescape_ics(text: str) -> str:
    """Unescape text characters from RFC 5545 format."""
    text = text.replace("\\n", "\n").replace("\\N", "\n")
    text = text.replace("\\,", ",").replace("\\;", ";")
    return text.replace("\\\\", "\\")


def parse_ics_date_time(raw_dt: str) -> Tuple[str, str]:
    """Extract YYYY-MM-DD and HH:MM from iCal DATE or DATE-TIME strings."""
    # Match YYYYMMDDTHHMMSS or YYYYMMDDTHHMM or YYYYMMDD, removing trailing Z or TZ offsets
    clean = re.sub(r"^.*:", "", raw_dt).strip().rstrip("Z")
    clean = re.sub(r"[+-]\d{2}:?\d{2}$", "", clean)
    m = re.match(r"^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2}))?", clean)
    if not m:
        now = datetime.now()
        return now.strftime("%Y-%m-%d"), "09:00"
    year, month, day = m.group(1), m.group(2), m.group(3)
    hour = m.group(4) or "09"
    minute = m.group(5) or "00"
    return f"{year}-{month}-{day}", f"{hour}:{minute}"


def parse_ics_trigger(trigger: str) -> int:
    """Parse VALARM TRIGGER duration like -PT15M, -PT1H, -P1D into minutes."""
    clean = trigger.upper().strip()
    if not clean or clean == "0" or clean == "PT0M":
        return 0
    if "-P1D" in clean or "P1D" in clean:
        return 1440
    m_hours = re.search(r"(\d+)H", clean)
    if m_hours:
        return int(m_hours.group(1)) * 60
    m_mins = re.search(r"(\d+)M", clean)
    if m_mins:
        mins = int(m_mins.group(1))
        # Snap to nearest valid ALPORA reminder
        valid_reminders = [0, 5, 10, 15, 30, 60, 1440]
        return min(valid_reminders, key=lambda r: abs(r - mins))
    return 15


def export_to_ics(events: List[Dict[str, Any]], tasks: List[Dict[str, Any]]) -> str:
    """Export planner events and tasks to a valid RFC 5545 iCalendar string."""
    now_utc = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//ALPORA//Day Planner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]

    for ev in events:
        ev_id = ev.get("id") or uuid.uuid4().hex
        ev_date = ev.get("date", "").replace("-", "")
        ev_time = ev.get("time", "09:00").replace(":", "") + "00"
        dtstart = f"{ev_date}T{ev_time}"
        title = escape_ics(ev.get("title", "Event"))

        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{ev_id}@alpora.local",
            f"DTSTAMP:{now_utc}",
            f"DTSTART:{dtstart}",
            f"SUMMARY:{title}",
        ])

        remind = ev.get("remind")
        if remind is not None and isinstance(remind, int):
            if remind == 0:
                trig = "PT0M"
            elif remind == 1440:
                trig = "-P1D"
            elif remind >= 60:
                trig = f"-PT{remind // 60}H"
            else:
                trig = f"-PT{remind}M"
            lines.extend([
                "BEGIN:VALARM",
                "ACTION:DISPLAY",
                f"DESCRIPTION:{title}",
                f"TRIGGER:{trig}",
                "END:VALARM",
            ])

        lines.append("END:VEVENT")

    for tk in tasks:
        tk_id = tk.get("id") or uuid.uuid4().hex
        tk_date = tk.get("date", "").replace("-", "")
        title = escape_ics(tk.get("title", "Task"))
        status = "COMPLETED" if tk.get("done") else "NEEDS-ACTION"

        lines.extend([
            "BEGIN:VTODO",
            f"UID:{tk_id}@alpora.local",
            f"DTSTAMP:{now_utc}",
            f"DUE;VALUE=DATE:{tk_date}",
            f"SUMMARY:{title}",
            f"STATUS:{status}",
            "END:VTODO",
        ])

    lines.append("END:VCALENDAR")
    lines.append("")
    return "\r\n".join(lines)


def import_from_ics(ics_content: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Parse an RFC 5545 iCalendar string into events and tasks."""
    lines = unfold_ics(ics_content)
    if not any("BEGIN:VCALENDAR" in l.upper() for l in lines):
        raise ConfigError("Invalid iCalendar file: Missing BEGIN:VCALENDAR")

    events: List[Dict[str, Any]] = []
    tasks: List[Dict[str, Any]] = []

    current_block: str | None = None
    item_props: Dict[str, str] = {}
    current_alarm: Dict[str, str] = {}
    in_alarm = False

    for line in lines:
        upper = line.strip().upper()
        if upper == "BEGIN:VEVENT":
            current_block = "VEVENT"
            item_props = {}
            in_alarm = False
        elif upper == "BEGIN:VTODO":
            current_block = "VTODO"
            item_props = {}
        elif upper == "BEGIN:VALARM" and current_block == "VEVENT":
            in_alarm = True
            current_alarm = {}
        elif upper == "END:VALARM":
            in_alarm = False
            if "TRIGGER" in current_alarm:
                item_props["_ALARM_TRIGGER"] = current_alarm["TRIGGER"]
        elif upper == "END:VEVENT" and current_block == "VEVENT":
            raw_summary = unescape_ics(item_props.get("SUMMARY", "Event")).strip()
            summary = raw_summary[:200].strip() or "Event"
            dt_raw = item_props.get("DTSTART", "")
            d_str, t_str = parse_ics_date_time(dt_raw)
            ev_id = item_props.get("UID", "").split("@")[0].strip() or uuid.uuid4().hex

            ev: Dict[str, Any] = {
                "id": ev_id,
                "date": d_str,
                "time": t_str,
                "title": summary,
            }
            if "_ALARM_TRIGGER" in item_props:
                ev["remind"] = parse_ics_trigger(item_props["_ALARM_TRIGGER"])
            events.append(ev)
            current_block = None
        elif upper == "END:VTODO" and current_block == "VTODO":
            raw_summary = unescape_ics(item_props.get("SUMMARY", "Task")).strip()
            summary = raw_summary[:200].strip() or "Task"
            dt_raw = item_props.get("DUE", item_props.get("DTSTART", ""))
            d_str, _ = parse_ics_date_time(dt_raw)
            tk_id = item_props.get("UID", "").split("@")[0].strip() or uuid.uuid4().hex
            status = item_props.get("STATUS", "").upper().strip()
            done = status == "COMPLETED"

            tasks.append({
                "id": tk_id,
                "date": d_str,
                "title": summary,
                "done": done,
            })
            current_block = None
        elif ":" in line:
            parts = line.split(":", 1)
            prop_key = parts[0].split(";")[0].upper().strip()
            prop_val = parts[1].strip()
            if in_alarm:
                current_alarm[prop_key] = prop_val
            elif current_block:
                item_props[prop_key] = prop_val

    return events, tasks
