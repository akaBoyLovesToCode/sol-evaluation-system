from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import app.utils.timezone as tz_module


def set_default_timezone(zone_name: str) -> None:
    tz_module.DEFAULT_TZ = ZoneInfo(zone_name)


def test_iso_local_converts_to_default_tz():
    set_default_timezone("Asia/Shanghai")
    dt = datetime(2025, 10, 24, 1, 0, 0, tzinfo=timezone.utc)
    assert tz_module.iso_local(dt) == "2025-10-24T09:00:00+08:00"


def test_iso_local_handles_naive_datetime():
    set_default_timezone("Asia/Shanghai")
    dt = datetime(2025, 10, 24, 18, 0, 0)
    assert tz_module.iso_local(dt) == "2025-10-25T02:00:00+08:00"


def test_resolve_timezone_offset():
    tz = tz_module.resolve_timezone(tz_offset="+09:00")
    dt = datetime(2025, 10, 24, 1, 0, 0, tzinfo=timezone.utc)
    assert tz_module.iso_local(dt, tz=tz) == "2025-10-24T10:00:00+09:00"
