"""
Gemalto / Veridos ID cards support

Class: GemaltoIDCard
Easy access: use read_and_retrieve_document() method to initialize card and retrieve document data
"""
from cards.base_card import BaseCard
from core.apdu import build_apdu, read_binary

from documents.id_document import IdDocument
from documents.id_parser import (
    parse_id_document,
    parse_id_personal,
    parse_id_residence,
    parse_id_portrait
)

ID_APP_AIDS = [
    bytes.fromhex("F381000002534552494401"),
    bytes.fromhex("F381000002534552494601"),
    bytes.fromhex("F381000002534552525001"),
]

class GemaltoIDCard(BaseCard):
    def init_card(self):
        """
        Select the correct ID application.
        Must be called before reading any files.

        Parameters:
            None
        Returns:
            None
        """
        for aid in ID_APP_AIDS:
            apdu = build_apdu(0x00, 0xA4, 0x04, 0x00, aid)
            rsp = self.pcsc.transmit(apdu)
            if rsp[-2:] == b"\x90\x00":
                return

        raise RuntimeError("Failed to select Gemalto ID application")

    def test(self) -> bool:
        """
        Tests if the card is a Gemalto card.

        Parameters:
            None
        Returns:
            bool: True if card is Gemalto, False otherwise
        """
        try:
            self.init_card()
            return True
        except Exception:
            return False


    def read(self):
        """
        Prepare the card for reading.
        Must be called before any file access.

        Parameters:
            None
        Returns:
            None
        """
        # REQUIRED for Gemalto / Veridos cards
        self.init_card()

    def _select_file(self, fid: bytes):
        """
        Select a file on the card.

        Parameters:
            fid (bytes): File ID
        Returns:
            None
        """
        apdu = build_apdu(0x00, 0xA4, 0x08, 0x00, fid)
        rsp = self.pcsc.transmit(apdu)

        if rsp[-2:] != b"\x90\x00":
            raise RuntimeError(f"SELECT FILE failed: {rsp.hex()}")


    def _read_file_internal(self, fid: bytes) -> bytes:
        """
        Read file from the card and return its data as bytes.

        Parameters:
            fid (bytes): File ID
        Returns:
            bytes: File data (bytes)
        """
        self._select_file(fid)

        # Read first 4 bytes = header
        header = read_binary(self.pcsc, 0, 4)
        if len(header) < 4:
            raise RuntimeError("File header too short")

        # Length is little-endian at bytes 2–3
        total_len = int.from_bytes(header[2:4], "little")

        offset = 4
        data = b""

        while len(data) < total_len:
            chunk = read_binary(self.pcsc, offset, total_len - len(data))
            if not chunk:
                break
            data += chunk
            offset += len(chunk)

        return data

    def _read_file(self, fid: bytes, allow_missing: bool = False) -> bytes:
        """
        Wrapper for _read_file_internal() function.
        Allows to return empty bytes if file not found (allow_missing=True - primarily for portrait photos).

        Parameters:
            fid (bytes): File ID
            allow_missing (bool): If True, return empty bytes if file not found
        Returns:
            bytes: File data (bytes)
        """
        try:
            return self._read_file_internal(fid)
        except Exception:
            if allow_missing:
                return b""
            raise

    def get_document(self) -> IdDocument:
        """
        Parse and format card data, and return IdDocument object.

        Parameters:
            None
        Returns:
            IdDocument: Document data as IdDocument object
        """

        doc = IdDocument()

        parse_id_document(self._read_file(b"\x0F\x02"), doc)
        parse_id_personal(self._read_file(b"\x0F\x03"), doc)
        parse_id_residence(self._read_file(b"\x0F\x04"), doc)

        photo_data = self._read_file(b"\x0F\x06", allow_missing=True)
        doc.portrait = parse_id_portrait(photo_data)

        return doc

    def read_and_retrieve_document(self):
        """
        Initialize (read) the card, and retrieve the document data.

        Parameters:
            None
        Returns:
            IdDocument: Document (card) data as IdDocument object
        """
        self.read()
        return self.get_document()

    # TEST:
    def test_read(self):
        """
        Test reading the card data.
        """
        DOC_FID = b"\x0F\x02"

        raw = self._read_file(DOC_FID)

        print("DOCUMENT FILE LEN:", len(raw))
        print("DOCUMENT FILE HEX (first 64):", raw[:64].hex())
        print("DOCUMENT FILE HEX (last 64):", raw[-64:].hex())
