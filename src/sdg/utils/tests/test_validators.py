from django.core.exceptions import ValidationError
from django.test import TestCase

from sdg.utils.validators import (
    validate_charfield_entry,
    validate_phone_number,
    validate_placeholders,
    validate_postal_code,
)


class ValidatorsTestCase(TestCase):
    """
    Validates the functions defined in ``utils.validators`` module.
    """

    def test_validate_charfield_entry_apostrophe_not_allowed(self):
        """
        Tests the ``validate_charfield_entry`` function when not explicitly
        allowing apostrophe character.
        """
        self.assertRaisesMessage(
            ValidationError,
            "Uw invoer bevat een ongeldig teken: '",
            validate_charfield_entry,
            "let's fail",
        )

    def test_validate_charfield_entry_apostrophe_allowed(self):
        """
        Tests the ``validate_charfield_entry`` function when explicitly
        allowing apostrophe character.
        """
        self.assertEqual(
            validate_charfield_entry("let's pass", allow_apostrophe=True), "let's pass"
        )

    def test_validate_postal_code(self):
        """
        Test all valid postal code and also test invalid values
        """
        invalid_postal_codes = [
            "0000AA",
            "0999AA",
            "1000  AA",
            "1000 AAA",
            "1000AAA",
            "0000aa",
            "0999aa",
            "1000  aa",
            "1000 aaa",
            "1000aaa",
            "1111,aa",
            "1111,a",
            '1111"a',
            '1111"aa',
        ]
        for invalid_postal_code in invalid_postal_codes:
            self.assertRaisesMessage(
                ValidationError,
                "Ongeldige postcode",
                validate_postal_code,
                invalid_postal_code,
            )

        self.assertIsNone(validate_postal_code("1015CJ"))
        self.assertIsNone(validate_postal_code("1015 CJ"))
        self.assertIsNone(validate_postal_code("1015cj"))
        self.assertIsNone(validate_postal_code("1015 cj"))
        self.assertIsNone(validate_postal_code("1015Cj"))
        self.assertIsNone(validate_postal_code("1015 Cj"))
        self.assertIsNone(validate_postal_code("1015cJ"))
        self.assertIsNone(validate_postal_code("1015 cJ"))

    def test_validate_phone_number(self):
        invalid_phone_numbers = [
            "0695azerty",
            "azerty0545",
            "@4566544++8",
            "onetwothreefour",
        ]
        for invalid_phone_number in invalid_phone_numbers:
            self.assertRaisesMessage(
                ValidationError,
                "Het opgegeven mobiele telefoonnummer is ongeldig.",
                validate_phone_number,
                invalid_phone_number,
            )

        self.assertEqual(validate_phone_number(" 0695959595"), " 0695959595")
        self.assertEqual(validate_phone_number("+33695959595"), "+33695959595")
        self.assertEqual(validate_phone_number("00695959595"), "00695959595")
        self.assertEqual(validate_phone_number("00-69-59-59-59-5"), "00-69-59-59-59-5")
        self.assertEqual(validate_phone_number("00 69 59 59 59 5"), "00 69 59 59 59 5")

    def test_validate_placeholders(self):
        """
        Test all valid placeholders and also test invalid ones.
        """
        invalid_texts = [
            "test [name]",
            "test [example_placeholder]",
            "test [example_placeholder] test",
            "test [[placeholder]]",
            "test XX",
            "test xx",
            "test with XXX",
            "test with xxx",
            "test XXXXXX placeholder",
            "test xxxxxx placeholder",
            "test\n[markdown link](https://example.com)\n[name]",
        ]
        for text in invalid_texts:
            with self.subTest(invalid_text=text):
                self.assertTrue(validate_placeholders(text))

        valid_texts = [
            "test X",
            "test x",
            "test X not-a-placeholder",
            "test x not-a-placeholder",
            "test YY",
            "test yy",
            "test YYYYYY not-a-placeholder",
            "test yyyyyy not-a-placeholder",
            "[markdown link](https://example.com)",
            "test [markdown link](https://example.com) here",
            "test\n[markdown link](https://example.com)",
            "example\n[markdown link](https://example.com)\n",
            "example\n[markdown link](https://example.com)\nexample",
        ]
        for text in valid_texts:
            with self.subTest(invalid_text=text):
                self.assertFalse(validate_placeholders(text))
