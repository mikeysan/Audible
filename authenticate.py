import audible
import getpass
from pathlib import Path
import os
import sys

def main():
    USERNAME = input('User: ').strip()
    PASSWORD = getpass.getpass('Password: ').strip()
    COUNTRY_CODE = 'us'
    FILENAME = Path('auth') / 'audible_auth.txt'

    if not USERNAME or not PASSWORD:
        print("Username and password cannot be empty.")
        sys.exit(1)

    try:
        # Authorize and register in one step
        auth = audible.Authenticator.from_login(
            USERNAME,
            PASSWORD,
            locale=COUNTRY_CODE,
            with_username=False
        )
    except audible.AuthenticationError as e:
        print(f"Authentication failed: {e}")
        sys.exit(1)

    try:
        # Ensure the auth directory exists
        FILENAME.parent.mkdir(parents=True, exist_ok=True)
        # Save credentials to file
        auth.to_file(FILENAME)
        # Restrict file permissions (Unix-based systems)
        try:
            os.chmod(FILENAME, 0o600)
        except AttributeError:
            # os.chmod may not be available or behave differently on some systems
            pass
        print(f"Authentication details saved to {FILENAME}")
    except IOError as e:
        print(f"Failed to write authentication file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
