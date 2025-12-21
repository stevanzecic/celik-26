"""
PC/SC (Smart Card) wrapper

Class: PcscCard
Class methods:
    transmit(apdu: list[int]) - Transmit APDU to the card
    atr() - Get ATR value of the card
Functions:
    connect_first_card() - Connect to the first available reader
    fetch_readers_list() - Fetch list of connected readers
    connect_card(reader_name: str) - Connect to a specific reader given by name
"""
from smartcard.System import readers
from smartcard.Exceptions import CardConnectionException

class PcscCard:
    def __init__(self, connection):
        self.conn = connection

    def transmit(self, apdu: list[int]) -> bytes:
        """
        Transmit APDU to the card.

        Parameters:
            apdu (list[int]): APDU bytes
        Returns:
            bytes: Response data
        """
        data, sw1, sw2 = self.conn.transmit(apdu)
        return bytes(data + [sw1, sw2])

    def atr(self) -> bytes:
        """
        Get ATR value of the card.

        Parameters:
            None
        Returns:
            bytes: ATR value of the card
        """
        return bytes(self.conn.getATR())


def connect_first_card() -> PcscCard:
    """
    Connect to the first available reader.

    Returns:
        PcscCard: Card connection
    """
    r = readers()
    if not r:
        raise RuntimeError("No smart card readers found")

    if len(r) == 0:
        raise RuntimeError("No smart card readers found")
    reader = r[0]
    try:
        conn = reader.createConnection()
    except RuntimeError:
        raise RuntimeError("Failed to create card connection")
    try:
        conn.connect()
    except CardConnectionException:
        raise RuntimeError("Card not inserted in reader")

    return PcscCard(conn)

def fetch_readers_list() -> list[str]:
    """
    Fetch list of connected readers.

    Parameters:
        None
    Returns:
        list[str]: List of reader names
    """
    r = readers()
    if not r:
        raise RuntimeError("No smart card readers found")

    return [r[i].name for i in range(len(r))]

def connect_card(reader_name: str) -> PcscCard:
    """
    Connect to a specific reader given by name.

    Parameters:
        reader_name (str): Reader name
    Returns:
        PcscCard | None: Card connection or None if reader not found
    """
    r = readers()
    reader = None
    if not r:
        raise RuntimeError("No smart card readers found")

    for i in range(len(r)):
        if r[i].name == reader_name:
            reader = r[i]
            break
    if reader:
        conn = reader.createConnection()
        conn.connect()
        return PcscCard(conn)

    raise RuntimeError(f"Reader {reader_name} not found")