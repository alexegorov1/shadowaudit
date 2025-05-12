from datetime import datetime
import traceback
import uuid

def format_exception(exc: Exception, context: str = "") -> dict:
    return {
        "id": str(uuid.uuid4()),
        "type": type(exc).__name__,
        "message": str(exc),
        "context": context,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "trace": traceback.format_exc(limit=5)
    }
