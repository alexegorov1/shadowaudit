import psutil
import time
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
        try:
            now_utc = get_current_utc_timestamp()
            if not isinstance(now_utc, datetime):
                raise TypeError("get_current_utc_timestamp() must return datetime")
            collected_at = now_utc.isoformat()
        except Exception as e:
            raise RuntimeError(f"Failed to obtain current UTC timestamp: {e}")

        hostname = get_hostname() or "unknown_host"
        user = get_current_user() or "unknown_user"
        platform_name = get_system_platform() or "unknown_platform"

        boot_time_iso = "unknown"
        uptime_seconds = -1

        try:
            boot_ts = psutil.boot_time()
            uptime_seconds = int(time.time() - boot_ts)
            boot_time = datetime.fromtimestamp(boot_ts, tz=timezone.utc)
            boot_time_iso = boot_time.isoformat()
        except Exception:
            pass

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
