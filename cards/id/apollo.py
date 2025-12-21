"""
Support for Apollo ID cards

Class: ApolloIDCard
Easy access: use read_and_retrieve_document() method to initialize card and retrieve document data
"""
import struct
from cards.base_card import BaseCard
from cards.id.atr import APOLLO_ATR
from documents.id_document import IdDocument
from documents.id_parser import (
    parse_id_document,
    parse_id_personal,
    parse_id_residence,
    parse_id_portrait
)

class ApolloIDCard(BaseCard):
    CARD_NAME = "ApolloIDCard"

    def init_card(self):
        """
        Apollo card object initialization. (No AID selection required)

        Parameters:
            None
        Returns:
            None
        """
        # Apollo cards do NOT require AID selection
        return

    def test(self) -> bool:
        """
        Tests if the card is an Apollo card.

        Parameters:
            None
        Returns:
            bool: True if card is Apollo, False otherwise
        """
        # Apollo cards have a fixed ATR
        return self.pcsc.atr() == APOLLO_ATR

    def read(self):
        """
        Reads the card data (with initialization).

        Parameters:
            None
        Returns:
            None
        """
        self.init_card()

    def _read_file(self, fid: bytes) -> bytes:
        """
        Read file from the card and return its data as bytes.

        Parameters:
            fid (bytes): File ID
        Returns:
            bytes: File data (bytes)
        """
        # SELECT FILE (same as Go)
        self._select_file(fid, p1=0x08, p2=0x00)

        # Apollo header is 6 bytes
        header = self._read_binary(0, 6)
        if len(header) < 6:
            raise RuntimeError("File header too short")

        length = struct.unpack("<H", header[4:6])[0]
        offset = 6

        out = bytearray()

        while length > 0:
            chunk = self._read_binary(offset, length)
            if not chunk:
                break
            out.extend(chunk)
            offset += len(chunk)
            length -= len(chunk)

        return bytes(out)

    def get_document(self) -> IdDocument:
        """
        Process values retrieved from the card (parse and format), and return IdDocument object.

        Parameters:
            None
        Returns:
            IdDocument: Document data as IdDocument object
        """
        doc = IdDocument()

        parse_id_document(self._read_file(b"\x0F\x02"), doc)
        parse_id_personal(self._read_file(b"\x0F\x03"), doc)
        parse_id_residence(self._read_file(b"\x0F\x04"), doc)

        try:
            photo_data = self._read_file(b"\x0F\x06")
            doc.portrait = parse_id_portrait(photo_data)
        except Exception:
            doc.portrait = None

        return doc

    def read_and_retrieve_document(self):
        """
        Initialize (read) the card, and retrieve the document data.
        Combines read() and get_document() methods for easy access.

        Parameters:
            None
        Returns:
            IdDocument: Document (card) data as IdDocument object
        """
        self.read()
        return self.get_document()

