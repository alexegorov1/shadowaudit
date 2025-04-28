import socket
import platform
import getpass
import time
from datetime import datetime, timezone
import psutil

def collect_basic_metadata() -> dict:
    hostname = socket.gethostname()
    platform_name = platform.system()
    user = getpass.getuser()
    boot_ts = psutil.boot_time()
    now_utc = datetime.utcnow().replace(tzinfo=timezone.utc)
    uptime = int(time.time() - boot_ts)
    boot_time = datetime.fromtimestamp(boot_ts, tz=timezone.utc).isoformat()

    return {
        "host_id": hostname,
        "source": "system_metadata",
        "collected_at": now_utc.isoformat(),
        "artifact_type": "basic_system_info",
        "confidence": 1.0,
        "evidence_type": "environmental",
        "hostname": hostname,
        "platform": platform_name,
        "user": user,
        "uptime": uptime,
        "boot_time": boot_time
    }
