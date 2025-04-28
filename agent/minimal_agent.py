import socket
import platform
import getpass
import time
from datetime import datetime, timezone
import psutil

def collect_basic_metadata() -> dict:
    now = datetime.utcnow().replace(tzinfo=timezone.utc)
    hostname = socket.gethostname()
    user = getpass.getuser()
    system = platform.system()
    boot_time = psutil.boot_time()
    uptime = int(now.timestamp() - boot_time)

    return {
        "host_id": hostname,
        "source": "system_metadata",
        "collected_at": now.isoformat(),
        "artifact_type": "basic_system_info",
        "confidence": 1.0,
        "evidence_type": "environmental",
        "hostname": hostname,
        "platform": system,
        "user": user,
        "uptime": uptime,
        "boot_time": datetime.fromtimestamp(boot_time, tz=timezone.utc).isoformat()
    }
