import socket
import getpass
import platform
import time
from datetime import datetime, timezone
import psutil
from core.interfaces import BaseCollector

class BasicInfoCollector(BaseCollector):
    def get_name(self) -> str:
        return "basic_info"

    def collect(self) -> list[dict]:
        hostname = socket.gethostname()
        user = getpass.getuser()
        system_platform = platform.system()
        boot_time_ts = psutil.boot_time()
        current_time_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
        collected_at = current_time_utc.isoformat()
        boot_time_iso = datetime.fromtimestamp(boot_time_ts, tz=timezone.utc).isoformat()
        uptime_seconds = int(current_time_utc.timestamp() - boot_time_ts)

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
            "boot_time": boot_time_iso,
            "uptime": uptime_seconds
        }

        return [artifact]
