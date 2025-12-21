"""
Generic card support (base class)
"""
from core.pcsc import PcscCard
from core.atr import Atr
from core.apdu import build_apdu, read_binary


class BaseCard:
    def __init__(self, pcsc: PcscCard):
        self.pcsc = pcsc
        self._atr = Atr(pcsc.atr())

    @property
    def atr(self) -> Atr:
        """
        Get ATR value of the card.

        Parameters:
            None
        Returns:
            Atr: ATR value of the card (Atr object)
        """
        return self._atr

    def test(self) -> bool:
        """
        Tests if the card is supported.

        Parameters:
            None
        Returns:
            bool: True if card is supported, False otherwise
        """
        raise NotImplementedError

    def read(self):
        """
        Reads the card data.

        Parameters:
            None
        Returns:
            None
        """
        raise NotImplementedError

    def _select_file(self, fid: bytes, p1=0x00, p2=0x00):
        """
        Select a file on the card.

        Parameters:
            fid (bytes): File ID
            p1 (int): P1 parameter
            p2 (int): P2 parameter
        Returns:
            None
        """
        apdu = build_apdu(0x00, 0xA4, p1, p2, fid)
        rsp = self.pcsc.transmit(apdu)

        if rsp[-2:] != b"\x90\x00":
            raise RuntimeError(f"SELECT FILE failed: {rsp.hex()}")

    def _read_file(self, fid: bytes, *, p1=0x00, p2=0x00) -> bytes:
        """
        Read file from the card and return its data as bytes.

        Parameters:
            fid (bytes): File ID
            p1 (int): P1 parameter
            p2 (int): P2 parameter
        Returns:
            bytes: File data (bytes)
        """
        self._select_file(fid, p1, p2)

        header = read_binary(self.pcsc, 0, 4)
        if len(header) < 4:
            raise RuntimeError("File header too short")

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

    def get_document(self):
        """
        Parse and format card data, and return a document object.

        Parameters:
            None
        Returns:
            Document: Document data as a document object
        """
        raise NotImplementedError

    def read_and_retrieve_document(self):
        """
        Initialize (read) the card, and retrieve the document data.

        Parameters:
            None
        Returns:
            Document: Document (card) data as a document object
        """
        raise NotImplementedError

