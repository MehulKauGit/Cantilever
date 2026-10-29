import shutil
import os
from db.database import DEFAULT_DB_PATH

def backup_database(destination_path: str, source_path: str = None) -> bool:
    """Backup SQLite database file to destination_path."""
    if source_path is None:
        source_path = DEFAULT_DB_PATH
    try:
        shutil.copy2(source_path, destination_path)
        return True
    except Exception as e:
        print(f"Error backing up database: {e}")
        return False

def restore_database(source_path: str, target_path: str = None) -> bool:
    """Restore SQLite database file from source_path."""
    if target_path is None:
        target_path = DEFAULT_DB_PATH
    try:
        shutil.copy2(source_path, target_path)
        return True
    except Exception as e:
        print(f"Error restoring database: {e}")
        return False
