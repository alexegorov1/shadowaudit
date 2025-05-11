import socket
import platform
import getpass
import time
from datetime import datetime, timezone
import psutil

def collect_basic_metadata() -> dict:
    now_utc = datetime.now(timezone.utc)
    hostname = socket.gethostname()
    user = getpass.getuser()
    system = platform.system()
    boot_ts = psutil.boot_time()
    uptime = int(time.time() - boot_ts)

    return {
        "host_id": hostname,
        "source": "system_metadata",
        "collected_at": now_utc.isoformat(),
        "artifact_type": "system_metadata",
        "confidence": 1.0,
        "evidence_type": "environmental",
        "hostname": hostname,
        "platform": system,
        "user": user,
        "uptime": uptime,
        "boot_time": datetime.fromtimestamp(boot_ts, tz=timezone.utc).isoformat()
    }
