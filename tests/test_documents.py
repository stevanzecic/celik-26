import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from documents.id_document import IdDocument
from documents.id_parser import parse_id_personal
from documents.medical_document import (
    InvalidCardNumber,
    InvalidInsurantNumber,
    MedicalDocument,
    RfzoParseError,
)
from documents.medical_parser import (
    parse_medical_document,
    parse_medical_fixed_personal,
    parse_medical_variable_admin,
    parse_medical_variable_personal,
)


def record(tag: int, value: bytes) -> bytes:
    return tag.to_bytes(2, "little") + len(value).to_bytes(2, "little") + value


def records(*items: tuple[int, bytes]) -> bytes:
    return b"".join(record(tag, value) for tag, value in items)


def utf16(value: str) -> bytes:
    return value.encode("utf-16")


class IdParserTests(unittest.TestCase):
    def test_legacy_purpose_of_stay_tag_is_supported(self):
        doc = IdDocument()
        parse_id_personal(records((1582, b"BORAVAK")), doc)
        self.assertEqual(doc.purpose_of_stay, "BORAVAK")

    def test_address_matches_official_reader_order_and_keeps_details(self):
        doc = IdDocument(
            place="BAJINA BAŠTA",
            community="BAJINA BAŠTA",
            street="DRAGUTINA I RADA ČUČKOVIĆ",
            house_number="016",
            entrance="A",
            floor="2",
            apartment_number="7",
        )
        self.assertEqual(
            doc.address(),
            "BAJINA BAŠTA, BAJINA BAŠTA, DRAGUTINA I RADA ČUČKOVIĆ 016, "
            "ulaz A, sprat 2, stan 7",
        )


class MedicalParserTests(unittest.TestCase):
    def setUp(self):
        self.doc = MedicalDocument()

    def test_complete_reference_tag_mapping(self):
        parse_medical_document(
            records(
                (1553, utf16("РФЗО")),
                (1554, b"06110101000000"),
                (1555, b"12345678901"),
                (1557, b"01012020"),
                (1558, b"01012030"),
                (1559, b"1234567890123456"),
                (1560, b"SR"),
            ),
            self.doc,
        )
        parse_medical_fixed_personal(
            records(
                (1569, b"12345678901"),
                (1570, utf16("Перић")),
                (1571, utf16("Perić")),
                (1572, utf16("Петар")),
                (1573, utf16("Petar")),
                (1574, b"01011990"),
            ),
            self.doc,
        )
        parse_medical_variable_personal(
            records((1586, b"31122025"), (1587, b"1")),
            self.doc,
        )
        parse_medical_variable_admin(
            records(
                (1601, utf16("Марко")),
                (1602, utf16("Marko")),
                (1603, b"02"),
                (1604, b"0101990710020"),
                (1605, utf16("Кнеза Милоша")),
                (1606, b"11000"),
                (1607, utf16("Врачар")),
                (1608, utf16("Београд")),
                (1609, b"00123"),
                (1610, utf16("5")),
                (1611, utf16("A")),
                (1612, utf16("12")),
                (1614, b"123"),
                (1615, utf16("Самостална делатност")),
                (1616, utf16("Дете")),
                (1617, b"1"),
                (1618, b"0101990710020"),
                (1619, b"10987654321"),
                (1620, utf16("Перић")),
                (1621, utf16("Perić")),
                (1622, utf16("Петар")),
                (1623, utf16("Petar")),
                (1624, b"15062021"),
                (1626, utf16("Србија")),
                (1630, utf16("Петар Перић")),
                (1631, utf16("Београд")),
                (1633, b"0101990710020"),
                (1634, b"6201"),
            ),
            self.doc,
        )

        self.assertEqual(self.doc.insurer_name, "РФЗО")
        self.assertEqual(self.doc.chip_serial_number, "1234567890123456")
        self.assertEqual(self.doc.first_name_latin, "Petar")
        self.assertEqual(self.doc.parent_name_latin, "Marko")
        self.assertEqual(self.doc.valid_until, "31.12.2025.")
        self.assertTrue(self.doc.permanently_valid)
        self.assertEqual(self.doc.gender, "F")
        self.assertEqual(self.doc.post_number, "11000")
        self.assertEqual(self.doc.street_code, "00123")
        self.assertEqual(self.doc.number, "5")
        self.assertEqual(self.doc.carrier_given_name_latin, "Petar")
        self.assertEqual(self.doc.carrier_insurant_number, "10987654321")
        self.assertEqual(self.doc.insurance_basis_rzzo, "123")
        self.assertEqual(self.doc.insurance_start_date, "15.06.2021.")
        self.assertEqual(self.doc.taxpayer_id_number, "0101990710020")

    def test_missing_gender_is_not_reported_as_female(self):
        parse_medical_variable_admin(record(1604, b"123"), self.doc)
        self.assertEqual(self.doc.gender, "")

    def test_rfzo_json_parser(self):
        self.assertEqual(
            MedicalDocument._parse_rfzo_payload(
                [{"zk_overena_do": "31.12.2026."}]
            ),
            "31.12.2026.",
        )
        with self.assertRaises(RfzoParseError):
            MedicalDocument._parse_rfzo_payload([])

    def test_rfzo_parser_normalizes_date_and_rejects_invalid_payload(self):
        self.assertEqual(
            MedicalDocument._parse_rfzo_payload(
                {"zk_overena_do": " 1.2.2027 "}
            ),
            "01.02.2027.",
        )
        for payload in (None, "unexpected", {}, [{"zk_overena_do": "missing"}]):
            with self.subTest(payload=payload), self.assertRaises(RfzoParseError):
                MedicalDocument._parse_rfzo_payload(payload)

    def test_rfzo_update_validates_identifiers_and_tracks_result(self):
        with self.assertRaises(InvalidCardNumber):
            MedicalDocument().update_from_rfzo()
        with self.assertRaises(InvalidInsurantNumber):
            MedicalDocument(card_id="12345678901").update_from_rfzo()

        response = Mock()
        response.json.return_value = [{"zk_overena_do": "31.12.2026."}]
        doc = MedicalDocument(
            card_id="12345678901",
            insurant_number="10987654321",
        )
        get = Mock(return_value=response)
        with patch.dict("sys.modules", {"requests": SimpleNamespace(get=get)}):
            result = doc.update_from_rfzo(timeout=5)

        self.assertEqual(result, "31.12.2026.")
        self.assertTrue(doc.rfzo_checked)
        self.assertEqual(doc.rfzo_valid_until, "31.12.2026.")
        response.raise_for_status.assert_called_once_with()
        get.assert_called_once_with(
            "https://rfzo.rs/api_overa.php",
            params={"kzo": "12345678901", "lbo": "10987654321"},
            headers={
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://rfzo.rs/",
                "User-Agent": "Mozilla/5.0",
            },
            timeout=(4, 5),
        )

    def test_rfzo_update_rejects_invalid_json(self):
        response = Mock()
        response.json.side_effect = ValueError("invalid JSON")
        get = Mock(return_value=response)
        doc = MedicalDocument(
            card_id="12345678901",
            insurant_number="10987654321",
        )

        with patch.dict("sys.modules", {"requests": SimpleNamespace(get=get)}):
            with self.assertRaisesRegex(RfzoParseError, "invalid JSON"):
                doc.update_from_rfzo()

    def test_rfzo_update_reports_html_response_as_service_issue(self):
        response = Mock()
        response.headers = {"Content-Type": "text/html; charset=UTF-8"}
        response.json.side_effect = ValueError("invalid JSON")
        get = Mock(return_value=response)
        doc = MedicalDocument(
            card_id="12345678901",
            insurant_number="10987654321",
        )

        with patch.dict("sys.modules", {"requests": SimpleNamespace(get=get)}):
            with self.assertRaisesRegex(RfzoParseError, "returned a web page"):
                doc.update_from_rfzo()


if __name__ == "__main__":
    unittest.main()
