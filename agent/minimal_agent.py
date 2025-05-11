import socket
import platform
import getpass
from datetime import datetime, timezone
import psutil

def collect_basic_metadata() -> dict:
    now = datetime.now(timezone.utc)
    hostname = socket.gethostname()
    user = getpass.getuser()
    system = platform.system()
    boot_time = datetime.fromtimestamp(psutil.boot_time(), tz=timezone.utc)
    uptime = int((now - boot_time).total_seconds())

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
