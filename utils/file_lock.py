import contextlib
import os
import time
from filelock import FileLock

@contextlib.contextmanager
def safe_file_operation(file_path):
    """Context manager for safe file operations with locking."""
    lock_path = f"{file_path}.lock"
    lock = FileLock(lock_path, timeout=10)  # 10 second timeout
    try:
        with lock:
            yield
    finally:
        if os.path.exists(lock_path):
            try:
                os.remove(lock_path)
            except:
                pass
