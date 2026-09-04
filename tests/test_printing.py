import unittest
from datetime import datetime

from documents.id_document import IdDocument
from gui.id_card_printer import (
    build_id_print_data,
    document_number_for_print,
    is_printable_card_data,
)


class IdCardPrintingTests(unittest.TestCase):
    def test_only_loaded_id_card_data_is_printable(self):
        document = IdDocument()
        self.assertTrue(is_printable_card_data({"type": "ID", "data": document}))
        self.assertTrue(is_printable_card_data({"type": "id", "data": document}))
        self.assertFalse(is_printable_card_data({"type": "MED", "data": document}))
        self.assertFalse(is_printable_card_data({"type": "ID", "data": None}))
        self.assertFalse(is_printable_card_data(None))

    def test_print_data_contains_expected_values(self):
        doc = IdDocument(
            document_name="TEST DOCUMENT NAME",
            surname="TEST_SURNAME",
            given_name="TEST_GIVEN_NAME",
            parent_given_name="TEST_PARENT_NAME",
            date_of_birth="01.01.2000.",
            place_of_birth="TEST PLACE OF BIRTH",
            community_of_birth="TEST COMMUNITY OF BIRTH",
            state_of_birth="TEST STATE OF BIRTH",
            place="TEST PLACE",
            community="TEST COMMUNITY",
            street="TEST STREET NAME",
            house_number="012",
            sex="S",
            issuing_authority="ISSUING AUTHORITY",
            document_serial_number="ID123456789",
            issuing_date="01.01.2000.",
            expiry_date="01.01.2000.",
        )

        data = build_id_print_data(doc, datetime(2026, 9, 1))

        self.assertEqual(data["document_name"], "TEST DOCUMENT NAME")
        self.assertEqual(data["print_date"], "01.09.2026.")
        self.assertIn(("Prezime:", "TEST_SURNAME"), data["citizen_rows"])
        self.assertIn(("Datum promene adrese:", "Nije dostupno"), data["citizen_rows"])
        self.assertIn(("Broj dokumenta:", "123456789"), data["document_rows"])

    def test_document_number_prefix_is_removed_only_for_expected_format(self):
        self.assertEqual(document_number_for_print("ID123456789"), "123456789")
        self.assertEqual(document_number_for_print("id 123456789"), "123456789")
        self.assertEqual(document_number_for_print("ID123"), "ID123")
        self.assertEqual(document_number_for_print("AB123456789"), "AB123456789")


if __name__ == "__main__":
    unittest.main()