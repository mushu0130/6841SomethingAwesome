import os
from datetime import datetime
from passwords import fetch_passwords, get_master_key
from autofill import fetch_autofill_data
from history import fetch_browsing_history

# Paths for each Chromium-based browser
BROWSER_PATHS = {
    "Chrome": r"%LOCALAPPDATA%\Google\Chrome\User Data",
    "Edge": r"%LOCALAPPDATA%\Microsoft\Edge\User Data",
    "Brave": r"%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data",
    "Opera": r"%APPDATA%\Opera Software\Opera Stable",
    "Vivaldi": r"%LOCALAPPDATA%\Vivaldi\User Data"
}

def create_logging_directory():
    """
    Creates a new directory in the Documents folder for storing the output files.
    Returns:
        str: Path to the newly created directory.
    """
    documents_path = os.path.expandvars(r"%USERPROFILE%\Desktop")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    logging_dir = os.path.join(documents_path, f"ChromeDataExtraction_{timestamp}")
    os.makedirs(logging_dir, exist_ok=True)
    return logging_dir

def log_to_file(file_path, data):
    """
    Writes data to the specified file.
    Args:
        file_path (str): Path to the file where data will be written.
        data (str): Data to be written to the file.
    """
    with open(file_path, "a", encoding="utf-8") as f:
        f.write(data + "\n")

def run_all_extractions(browser_name, browser_path, logging_dir):
    """
    Runs all extraction functions (passwords, autofill, history) for a given browser
    and logs the results to files in the specified logging directory.
    """
    print(f"\nExtracting data from {browser_name}...")
    browser_log_dir = os.path.join(logging_dir, browser_name)
    os.makedirs(browser_log_dir, exist_ok=True)

    # Check if the master key is available
    master_key = get_master_key(browser_path)
    if master_key is None:
        print(f"Skipping {browser_name} due to missing or invalid master key.")
        return

    # Run each extraction module and log results
    try:
        # Passwords
        passwords_log_path = os.path.join(browser_log_dir, "passwords.txt")
        passwords_data = fetch_passwords(browser_path)
        log_to_file(passwords_log_path, passwords_data)

        # Autofill Data
        autofill_log_path = os.path.join(browser_log_dir, "autofill.txt")
        autofill_data = fetch_autofill_data(browser_path)
        log_to_file(autofill_log_path, autofill_data)

        # Browsing History
        history_log_path = os.path.join(browser_log_dir, "history.txt")
        history_data = fetch_browsing_history(browser_path)
        log_to_file(history_log_path, history_data)

    except Exception as e:
        print(f"Error retrieving data from {browser_name}: {e}")

def fetch_data_from_all_browsers():
    """
    Attempts to fetch data from all available Chromium-based browsers and log results
    to a new directory in the Documents folder.
    """
    logging_dir = create_logging_directory()
    for browser_name, browser_path in BROWSER_PATHS.items():
        expanded_path = os.path.expandvars(browser_path)
        if os.path.exists(expanded_path):
            run_all_extractions(browser_name, expanded_path, logging_dir)
        else:
            print(f"{browser_name} is not installed or the path does not exist.")

# Run the function to fetch and display data from all available browsers
fetch_data_from_all_browsers()
