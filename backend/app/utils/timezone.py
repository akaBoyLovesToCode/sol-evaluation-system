"""Timezone utilities for consistent UTC storage and localized serialization."""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Optional

from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

DEFAULT_TZ_NAME = os.getenv("APP_DEFAULT_TZ", "Asia/Shanghai")
try:
    DEFAULT_TZ = ZoneInfo(DEFAULT_TZ_NAME)
except ZoneInfoNotFoundError:
    DEFAULT_TZ = ZoneInfo("UTC")


def utcnow() -> datetime:
    """Return the current time in UTC as an aware datetime."""

    return datetime.now(timezone.utc)


def _ensure_aware(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def resolve_timezone(tz_name: Optional[str] = None, tz_offset: Optional[str] = None) -> timezone:
    """Resolve the desired timezone from a name or offset string."""

    if tz_name:
        try:
            return ZoneInfo(tz_name)
        except ZoneInfoNotFoundError:
            pass

    if tz_offset:
        try:
            sign = 1 if tz_offset.startswith("+") else -1
            hours_minutes = tz_offset[1:].split(":")
            hours = int(hours_minutes[0])
            minutes = int(hours_minutes[1]) if len(hours_minutes) > 1 else 0
            delta = timedelta(hours=hours, minutes=minutes)
            return timezone(sign * delta)
        except (ValueError, IndexError):
            pass

    return DEFAULT_TZ


def resolve_timezone_from_request(args) -> timezone:
    """Resolve timezone using Flask request args (tz or tz_offset)."""

    tz_name = args.get("tz") if args else None
    tz_offset = args.get("tz_offset") if args else None
    return resolve_timezone(tz_name, tz_offset)


def to_local(dt: datetime | None, tz: Optional[timezone] = None) -> datetime | None:
    """Convert a datetime to the requested timezone (default UTC+8)."""

    aware = _ensure_aware(dt)
    if aware is None:
        return None
    target_tz = tz or DEFAULT_TZ
    return aware.astimezone(target_tz)


def iso_local(dt: datetime | None, tz: Optional[timezone] = None) -> Optional[str]:
    """Return an ISO-formatted string (seconds precision) in the desired timezone."""

    local_dt = to_local(dt, tz=tz)
    return local_dt.isoformat(timespec="seconds") if local_dt else None


def iso_date(dt: datetime | None, tz: Optional[timezone] = None) -> Optional[str]:
    """Return a date-only ISO string from a datetime or date."""

    if dt is None:
        return None
    if isinstance(dt, datetime):
        local_dt = to_local(dt, tz=tz)
        return local_dt.date().isoformat() if local_dt else None
    return dt.isoformat()


def timezone_label(tz: timezone) -> str:
    """Return a human-readable label for a timezone object."""

    if isinstance(tz, ZoneInfo):
        return tz.key
    name = tz.tzname(None)
    if name:
        return name
    offset = tz.utcoffset(None)
    if offset is None:
        return DEFAULT_TZ.key if isinstance(DEFAULT_TZ, ZoneInfo) else "UTC"
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    hours, minutes = divmod(total_minutes, 60)
    return f"UTC{sign}{hours:02d}:{minutes:02d}"
