import unittest
from unittest.mock import MagicMock, patch

from cards.detector import detect_card
from cards.id.apollo import ApolloIDCard
from cards.id.atr import GEMALTO_ATRS
from cards.id.gemalto import GemaltoIDCard
from cards.medical.medical import MEDICAL_ATRS


class BinaryFileCard:
    def __init__(self, payload: bytes, *, truncate=False):
        self.payload = payload
        self.truncate = truncate
        self.commands = []

    def atr(self):
        return b"ATR"

    def transmit(self, apdu):
        self.commands.append(apdu)
        if apdu[1] == 0xA4:
            return b"\x90\x00"
        if apdu[1] != 0xB0:
            raise AssertionError(f"Unexpected APDU: {apdu}")

        offset = (apdu[2] << 8) | apdu[3]
        length = apdu[4] or 256
        header = b"\x00\x00\x00\x00" + len(self.payload).to_bytes(2, "little")
        file_data = header + self.payload
        chunk = file_data[offset:offset + length]
        if self.truncate and offset >= 6:
            chunk = b""
        return chunk + b"\x90\x00"


class CardProtocolTests(unittest.TestCase):
    def test_apollo_read_file_uses_read_binary_and_select_le_4(self):
        pcsc = BinaryFileCard(b"payload")
        card = ApolloIDCard(pcsc)
        self.assertEqual(card._read_file(b"\x0F\x02"), b"payload")
        self.assertEqual(
            pcsc.commands[0],
            [0x00, 0xA4, 0x08, 0x00, 0x02, 0x0F, 0x02, 0x04],
        )

    def test_apollo_rejects_truncated_file(self):
        card = ApolloIDCard(BinaryFileCard(b"payload", truncate=True))
        with self.assertRaisesRegex(RuntimeError, "truncated"):
            card._read_file(b"\x0F\x02")

    def test_gemalto_select_requests_four_response_bytes(self):
        pcsc = BinaryFileCard(b"")
        GemaltoIDCard(pcsc)._select_file(b"\x0F\x02")
        self.assertEqual(pcsc.commands[0][-1], 4)


class DetectorTests(unittest.TestCase):
    def test_shared_gemalto_atr_is_probed_and_can_be_medical(self):
        pcsc = MagicMock()
        pcsc.atr.return_value = next(iter(GEMALTO_ATRS))
        gemalto = MagicMock()
        gemalto.test.return_value = False
        medical = MagicMock()
        medical.test.return_value = True
        medical.read_and_retrieve_document.return_value = "medical-document"

        with patch("cards.detector.GemaltoIDCard", return_value=gemalto), patch(
            "cards.detector.MedicalCard", return_value=medical
        ):
            result = detect_card(pcsc)

        self.assertEqual(result, {"type": "MED", "data": "medical-document"})
        gemalto.test.assert_called_once_with()
        medical.test.assert_called_once_with()

    def test_unique_medical_atr_uses_medical_handler_directly(self):
        pcsc = MagicMock()
        pcsc.atr.return_value = next(iter(MEDICAL_ATRS))
        medical = MagicMock()
        medical.read_and_retrieve_document.return_value = "medical-document"

        with patch("cards.detector.MedicalCard", return_value=medical):
            result = detect_card(pcsc)

        self.assertEqual(result["type"], "MED")
        medical.test.assert_not_called()


if __name__ == "__main__":
    unittest.main()
