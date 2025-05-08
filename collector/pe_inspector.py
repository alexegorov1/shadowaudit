import pefile
import os

def is_pe_file(file_path: str) -> bool:
    try:
        if not os.path.isfile(file_path):
            return False
        with open(file_path, "rb") as f:
            if f.read(2) != b"MZ":
                return False
        pefile.PE(file_path, fast_load=True)
        return True
    except Exception:
        return False
