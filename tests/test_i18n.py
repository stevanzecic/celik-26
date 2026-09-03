import unittest

from gui.i18n import DEFAULT_LANGUAGE, tr


class TranslationTests(unittest.TestCase):
    def test_serbian_is_the_default(self):
        self.assertEqual(DEFAULT_LANGUAGE, "sr")
        self.assertEqual(tr("save", "sr"), "Sačuvaj")

    def test_english_translation_and_formatting(self):
        self.assertEqual(tr("save", "en"), "Save")
        self.assertEqual(
            tr("connected_reader", "en", name="Reader 1"),
            "Connected to reader: Reader 1",
        )

    def test_unknown_language_falls_back_to_serbian(self):
        self.assertEqual(tr("print", "de"), "Štampaj")


if __name__ == "__main__":
    unittest.main()
