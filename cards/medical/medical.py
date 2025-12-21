"""
Serbian Medical Card support

Class: MedicalCard
Easy access: use read_and_retrieve_document() method to initialize card and retrieve document data
"""
from cards.base_card import BaseCard
from core.tlv import parse_tlv
from core.apdu import build_apdu, read_binary
from documents.medical_document import MedicalDocument
from documents.medical_parser import (
    parse_medical_document,
    parse_medical_fixed_personal,
    parse_medical_variable_personal,
    parse_medical_variable_admin,
)

MEDICAL_ATRS = {
    bytes.fromhex("3BF41300008131FE4552465A4FED"),
    bytes.fromhex("3B9E978031FE4553434520382E302D433156300D0A6E"),
}

MEDICAL_AID = bytes.fromhex("F38100000253455256535A4B01")

MED_DOC = b"\x0D\x01"
MED_FIXED = b"\x0D\x02"
MED_VAR = b"\x0D\x03"
MED_ADMIN = b"\x0D\x04"


class MedicalCard(BaseCard):

    def test(self) -> bool:
        """
        Tests if the card is a Serbian Medical card.

        Parameters:
            None
        Returns:
            bool: True if card is Serbian Medical, False otherwise
        """
        try:
            apdu = build_apdu(0x00, 0xA4, 0x04, 0x00, MEDICAL_AID)
            rsp = self.pcsc.transmit(apdu)
            return rsp[-2:] == b"\x90\x00"
        except Exception:
            return False

    def init_card(self):
        """
        Select the correct Medical application.
        Must be called before reading any files.

        Parameters:
            None
        Returns:
            None
        """
        apdu = build_apdu(0x00, 0xA4, 0x04, 0x00, MEDICAL_AID)
        rsp = self.pcsc.transmit(apdu)
        if rsp[-2:] != b"\x90\x00":
            raise RuntimeError("Medical AID selection failed")

    def read(self):
        """
        Prepare the card for reading.
        Must be called before any file access.

        Parameters:
            None
        Returns:
            None
        """
        self.init_card()

        self._med_doc = self._read_file(MED_DOC)
        self._med_fixed = self._read_file(MED_FIXED)
        self._med_var = self._read_file(MED_VAR)
        self._med_admin = self._read_file(MED_ADMIN)

    def get_document(self) -> MedicalDocument:
        """
        Parse and format card data, and return MedicalDocument object.

        Parameters:
            None
        Returns:
            MedicalDocument: Document data as MedicalDocument object
        """
        doc = MedicalDocument()

        parse_medical_document(self._med_doc, doc)
        parse_medical_fixed_personal(self._med_fixed, doc)
        parse_medical_variable_personal(self._med_var, doc)
        parse_medical_variable_admin(self._med_admin, doc)

        raw = self._read_file(b"\x0D\x01")
        fields = parse_tlv(raw)

        print("MED DOC TLV TAGS:", sorted(fields.keys()))
        print("MED DOC RAW HEX (first 64):", raw[:64].hex())
        print("MED DOC RAW HEX (last 64):", raw[-64:].hex())

        return doc

    def read_and_retrieve_document(self):
        """
        Initialize (read) the card, and retrieve the document data.
        Combines read() and get_document() methods for easy access.

        Parameters:
            None
        Returns:
            MedicalDocument: Document (card) data as MedicalDocument object
        """
        self.read()
        return self.get_document()
