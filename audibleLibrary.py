import audible
import csv
import logging
from pathlib import Path
import sys

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("audibleLibrary.log"),
            logging.StreamHandler()
        ]
    )

def convert_time(runtime_minutes):
    """
    Convert runtime from minutes to a tuple of (total minutes, 'HH:MM' format).
    
    Args:
        runtime_minutes (int): Runtime in minutes.
    
    Returns:
        tuple: (runtime_minutes, runtime_hm)
    """
    try:
        hours = runtime_minutes // 60
        minutes = runtime_minutes % 60
        runtime_hm = f"{hours}:{str(minutes).zfill(2)}"
        return runtime_minutes, runtime_hm
    except (TypeError, ValueError) as e:
        logging.error(f"Error converting runtime: {e}")
        return 0, '0:00'

def get_contributors(contributors):
    """
    Extract contributor names from the contributors list.
    
    Args:
        contributors (list): List of contributor dictionaries.
    
    Returns:
        str: Semicolon-separated contributor names or 'N/A'.
    """
    try:
        contributor_names = [contributor['name'] for contributor in contributors]
        return ';'.join(contributor_names)
    except (TypeError, KeyError) as e:
        logging.error(f"Error retrieving contributors: {e}")
        return 'N/A'

def get_library(auth_file):
    """
    Retrieve the Audible library using the provided authentication file.
    
    Args:
        auth_file (Path): Path to the authentication file.
    
    Returns:
        list: List of book details.
    """
    if not auth_file.exists():
        logging.error(f"Authentication file not found at {auth_file}")
        sys.exit(1)

    try:
        AUTH = audible.Authenticator.from_file(auth_file)
    except audible.AuthenticationError as e:
        logging.error(f"Failed to authenticate: {e}")
        sys.exit(1)

    try:
        with audible.Client(auth=AUTH) as client:
            library = client.get(
                "1.0/library",
                num_results=1000,
                response_groups="product_desc, product_attrs, contributors",
                sort_by="Author"
            )
    except audible.APIError as e:
        logging.error(f"API request failed: {e}")
        sys.exit(1)

    book_list = []
    for book in library.get("items", []):
        authors = get_contributors(book.get('authors', []))
        narrators = get_contributors(book.get('narrators', []))
        title = book.get('title', 'Unknown Title')
        purchased = book.get('purchase_date', 'Unknown Purchase Date')
        released = book.get('release_date', 'Unknown Release Date')
        runtime_length = book.get('runtime_length_min', 0)
        runtime_mmm, runtime_hm = convert_time(runtime_length)
        book_list.append([authors, title, narrators, runtime_mmm, runtime_hm, released, purchased])

    return book_list

def write_library(library, output_file):
    """
    Write the library data to a CSV file.
    
    Args:
        library (list): List of book details.
        output_file (Path): Path to the output CSV file.
    """
    fields = ['authors', 'title', 'narrators', 'runtime_mmm', 'runtime_hm', 'released', 'purchased']
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with output_file.open('w', newline='', encoding='UTF8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(fields)
            writer.writerows(library)
        logging.info(f"Library data written to {output_file}")
    except IOError as e:
        logging.error(f"Failed to write CSV file: {e}")
        sys.exit(1)

def main():
    setup_logging()
    AUTH_FILE = Path('auth') / 'audible_auth.txt'
    OUTPUT_FILE = Path('data') / 'library.csv'

    logging.info("Starting Audible library retrieval.")
    library = get_library(AUTH_FILE)
    write_library(library, OUTPUT_FILE)
    logging.info("Audible library retrieval completed successfully.")

if __name__ == "__main__":
    main()
