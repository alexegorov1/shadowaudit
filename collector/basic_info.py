import psutil
from datetime import datetime, timezone
from core.interfaces import BaseCollector
from core.utils import (
    get_hostname,
    get_current_user,
    get_system_platform,
    get_current_utc_timestamp
)

class BasicInfoCollector(BaseCollector):
    def get_name(self) -> str:
        return "basic_info"

    def collect(self) -> list[dict]:
        now_utc = get_current_utc_timestamp()
        hostname = get_hostname()
        user = get_current_user()
        platform_name = get_system_platform()
        collected_at = now_utc.isoformat()

        boot_time_iso = "unknown"
        uptime_seconds = -1

        try:
            boot_ts = psutil.boot_time()
            uptime_seconds = int(now_utc.timestamp() - boot_ts)
            boot_time_iso = datetime.fromtimestamp(boot_ts, tz=timezone.utc).isoformat()

        artifact = {
            "host_id": hostname,
            "source": "basic_info",
            "collected_at": collected_at,
            "artifact_type": "system_metadata",
            "confidence": 1.0,
            "evidence_type": "environmental",
            "hostname": hostname,
            "user": user,
            "platform": platform_name,
            "boot_time": boot_time_iso,
            "uptime": uptime_seconds
        }

        return [artifact]
