import unittest

from core.apdu import build_apdu, read_binary
from core.encoding import _decode_utf16le, decode_ascii_date, format_date_ddmmyyyy
from core.tlv import parse_tlv


def tlv_record(tag: int, value: bytes) -> bytes:
    return tag.to_bytes(2, "little") + len(value).to_bytes(2, "little") + value


class ResponseCard:
    def __init__(self, response: bytes):
        self.response = response
        self.apdus = []

    def transmit(self, apdu):
        self.apdus.append(apdu)
        return self.response


class ApduTests(unittest.TestCase):
    def test_builds_short_apdu_and_encodes_le_256_as_zero(self):
        self.assertEqual(
            build_apdu(0x00, 0xA4, 0x04, 0x00, b"AB", 256),
            [0x00, 0xA4, 0x04, 0x00, 0x02, 0x41, 0x42, 0x00],
        )

    def test_rejects_values_that_cannot_be_encoded(self):
        with self.assertRaises(ValueError):
            build_apdu(256, 0, 0, 0)
        with self.assertRaises(ValueError):
            build_apdu(0, 0, 0, 0, b"x" * 256)
        with self.assertRaises(ValueError):
            build_apdu(0, 0, 0, 0, le=0)

    def test_read_binary_returns_payload_and_checks_status(self):
        card = ResponseCard(b"data\x90\x00")
        self.assertEqual(read_binary(card, 0x1234, 4), b"data")
        self.assertEqual(card.apdus, [[0x00, 0xB0, 0x12, 0x34, 0x04]])

        with self.assertRaises(RuntimeError):
            read_binary(ResponseCard(b"\x6A\x82"), 0, 1)

    def test_read_binary_validates_range(self):
        with self.assertRaises(ValueError):
            read_binary(ResponseCard(b"\x90\x00"), -1, 1)
        with self.assertRaises(ValueError):
            read_binary(ResponseCard(b"\x90\x00"), 0, -1)
        self.assertEqual(read_binary(ResponseCard(b"unused"), 0, 0), b"")


class TlvTests(unittest.TestCase):
    def test_parses_valid_records(self):
        data = tlv_record(1, b"abc") + tlv_record(2, b"")
        self.assertEqual(parse_tlv(data), {1: b"abc", 2: b""})

    def test_rejects_empty_and_truncated_data(self):
        for data in (b"", b"\x01", b"\x01\x00\x04\x00ab"):
            with self.subTest(data=data), self.assertRaises(ValueError):
                parse_tlv(data)


class EncodingTests(unittest.TestCase):
    def test_utf16_decoder_removes_bom(self):
        self.assertEqual(_decode_utf16le("Петар".encode("utf-16")), "Петар")
        self.assertEqual(_decode_utf16le("Petar".encode("utf-16le")), "Petar")

    def test_dates_match_reference_format(self):
        self.assertEqual(format_date_ddmmyyyy("01012030"), "01.01.2030.")
        self.assertEqual(decode_ascii_date(b"31122025"), "31.12.2025.")
        self.assertEqual(decode_ascii_date(b"not-date"), "")

    def test_unavailable_and_invalid_dates_are_empty(self):
        self.assertEqual(format_date_ddmmyyyy("01010001"), "")
        self.assertEqual(format_date_ddmmyyyy("31022030"), "")


if __name__ == "__main__":
    unittest.main()
