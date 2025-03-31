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
        boot_time = psutil.boot_time()
        uptime_seconds = int(time.time() - boot_time)
        boot_time_iso = datetime.fromtimestamp(boot_time, tz=timezone.utc).isoformat()
        collected_at = datetime.utcnow().replace(tzinfo=timezone.utc).isoformat()

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
            "uptime": uptime_seconds,
            "boot_time": boot_time_iso
        }

        return [artifact]
