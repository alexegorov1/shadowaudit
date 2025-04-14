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
        hostname = get_hostname()
        user = get_current_user()
        system_platform = get_system_platform()
        now_utc = get_current_utc_timestamp()
        collected_at = now_utc.isoformat()

        try:
            boot_ts = psutil.boot_time()
            uptime = int(now_utc.timestamp() - boot_ts)
            boot_time = datetime.fromtimestamp(boot_ts, tz=timezone.utc).isoformat()
        except Exception:
            uptime = -1
            boot_time = "unknown"

        artifact = {
            "host_id": hostname,
            "source": "basic_info",
            "collected_at": collected_at,
            "artifact_type": "system_metadata",
            "confidence": 1.0,
            "evidence_type": "environmental",
            "hostname": hostname,
            "user": user,
            "platform": system_platform,
            "boot_time": boot_time,
            "uptime": uptime
        }

        return [artifact]
