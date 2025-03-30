import socket
import platform
import getpass
import time
from datetime import datetime, timezone
import psutil

def collect_basic_metadata():
    hostname = socket.gethostname()
    system_platform = platform.system()
    user = getpass.getuser()
    boot_timestamp = psutil.boot_time()
    uptime_seconds = int(time.time() - boot_timestamp)
    boot_time_iso = datetime.fromtimestamp(boot_timestamp, tz=timezone.utc).isoformat()

    return {
        "host_id": hostname,
        "source": "system_metadata",
        "collected_at": datetime.utcnow().replace(tzinfo=timezone.utc).isoformat(),
        "artifact_type": "basic_system_info",
        "confidence": 1.0,
        "evidence_type": "environmental",
        "hostname": hostname,
        "platform": system_platform,
        "user": user,
        "uptime": uptime_seconds,
        "boot_time": boot_time_iso
    }
