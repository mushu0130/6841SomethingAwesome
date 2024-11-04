import os
import sqlite3
from datetime import datetime, timedelta
import tempfile
import shutil

def fetch_browsing_history(browser_path):
    """
    Connects to the browser's 'History' SQLite database to retrieve and return browsing history.
    This includes visited URLs, visit counts, and timestamps.

    Returns:
        str: Formatted browsing history data.
    """
    history_path = os.path.join(browser_path, "Default", "History")
    if not os.path.exists(history_path):
        return "No history file found."

    # Create a temporary copy of the database
    temp_dir = tempfile.gettempdir()
    temp_history_path = os.path.join(temp_dir, "History_copy")
    shutil.copy2(history_path, temp_history_path)

    conn = sqlite3.connect(temp_history_path)
    cursor = conn.cursor()

    # Fetch browsing history
    cursor.execute("SELECT url, title, visit_count, last_visit_time FROM urls")
    data = "Browsing History:\n"
    for row in cursor.fetchall():
        url, title, visit_count, last_visit_time = row
        # Convert WebKit timestamp to a readable format
        last_visit_time = datetime(1601, 1, 1) + timedelta(microseconds=last_visit_time)
        data += f"URL: {url}, Title: {title}, Visit Count: {visit_count}, Last Visit: {last_visit_time}\n"
        data += "-" * 40 + "\n"

    conn.close()
    os.remove(temp_history_path)
    return data
