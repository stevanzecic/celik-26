"""
Card reader and card reading CLI and API

CLI:
    python3 card_reader_cli.py -h - Show help
    python3 card_reader_cli.py -l - List connected card readers
    python3 card_reader_cli.py -a - Auto-detect reader and read card
    python3 card_reader_cli.py -r <READER_NAME> - Read card from specific reader
Functions:
    connect_first_reader() - Connect to the first available reader
    get_readers_list(override_exception: bool = False) - Fetch list of connected readers
    connect_reader(reader_name) - Connect to a specific reader given by name
    read_card(card_reader) - Read card in the given reader
    auto_read_card() - Detect card and read data from first available reader
"""

import argparse
from core.pcsc import PcscCard, connect_first_card, fetch_readers_list, connect_card
from cards.detector import detect_card
from cards.base_card import BaseCard


def connect_first_reader():
    """
    Connect to the first available reader.

    Returns:
        PcscCard: Card connection
    """
    card_reader = connect_first_card()
    return card_reader

def get_readers_list(override_exception: bool = False):
    """
    Fetch list of connected readers.

    Parameters:
        override_exception (bool): Override exception - prevents raising RuntimeError
    Returns:
        list[PcscCard]: List of connected card readers
    """
    reader_list = fetch_readers_list(override_exception=override_exception)
    return reader_list

def connect_reader(reader_name):
    """
    Connect to a specific reader given by name.

    Parameters:
        reader_name (str): Reader name

    Returns:
        PcscCard | None: Card connection or None if reader not found
    """
    card_reader = connect_card(reader_name)
    return card_reader

def read_card(card_reader: PcscCard):
    """
    Read card in the given reader.

    Parameters:
        card_reader (PcscCard): Card reader connection

    Returns:
        dict:    {"type": "ID" | "MED", "data": <CARD DATA>}
    """

    card_data = detect_card(card_reader)
    return card_data

def auto_read_card():
    """
    Detect card and read data from first available reader. Returns dictionary with card type and data.

    Returns:
        dict:    {"type": "ID" | "MED", "data": <CARD DATA>}
    """
    card_reader = connect_first_reader()
    card_data = read_card(card_reader)
    return card_data


def main():
    parser = argparse.ArgumentParser(
        description="Serbian smart card reader (ID / Medical / Vehicle)"
    )

    group = parser.add_mutually_exclusive_group(required=True)

    group.add_argument(
        "-l", "--list",
        action="store_true",
        help="List connected card readers",
    )

    group.add_argument(
        "-a", "--auto",
        action="store_true",
        help="Auto-detect reader and read card",
    )

    group.add_argument(
        "-r", "--read",
        metavar="READER_NAME",
        help="Read card from specific reader",
    )

    args = parser.parse_args()

    # ---------------- LIST READERS ----------------
    if args.list:
        readers = get_readers_list()
        if not readers:
            print("No card readers found.")
            return

        print("Connected readers:")
        for r in readers:
            print(f" - {r}")
        return

    # ---------------- AUTO READ ----------------
    if args.auto:
        try:
            doc = auto_read_card()
            print(doc)
        except Exception as e:
            print(f"Error reading card: {e}")
        return

    # ---------------- READ FROM SPECIFIC READER ----------------
    if args.read:
        reader = connect_reader(args.read)
        if not reader:
            print(f"Reader not found: {args.read}")
            return

        try:
            doc = read_card(reader)
            print(doc)
        except Exception as e:
            print(f"Error reading card: {e}")
        return


if __name__ == "__main__":
    main()