"""
MedicalDocument model for Serbian Medical Insurance Card.

- Holds data parsed directly from the card
- Provides explicit RFZO update on user action
- No UI logic
- No threading
"""

from dataclasses import dataclass, field
import requests
import re

RFZO_URL = "https://www.rfzo.rs/proveraUplateDoprinosa2.php"


class RfzoError(Exception):
    """Base RFZO error."""


class InvalidCardNumber(RfzoError):
    pass


class InvalidInsurantNumber(RfzoError):
    pass


class RfzoParseError(RfzoError):
    pass


@dataclass
class MedicalDocument:
    # -------- Card data (TLV parsed) --------

    insurer_name: str = ""
    insurer_id: str = ""
    card_id: str = ""

    first_name: str = ""
    first_name_latin: str = ""
    last_name: str = ""
    last_name_latin: str = ""
    parent_name: str = ""

    gender: str = ""
    jmbg: str = ""
    insurant_number: str = ""

    date_of_birth: str = ""
    date_of_issue: str = ""
    date_of_expiry: str = ""

    street: str = ""
    place: str = ""
    municipality: str = ""

    valid_until: str = ""
    permanently_valid: bool = False

    print_language: str = ""

    # -------- RFZO enriched data --------

    rfzo_valid_until: str | None = None
    rfzo_checked: bool = False

    # -------- Helpers --------

    def full_name_latin(self) -> str:
        return f"{self.first_name_latin} {self.parent_name} {self.last_name_latin}"

    def full_address(self) -> str:
        addr = f"{self.street}, {self.place}"
        if self.municipality:
            addr += f" ({self.municipality})"
        return addr

    # -------- RFZO UPDATE (MANUAL) --------

    def update_from_rfzo(self, timeout=8):
        if len(self.card_id) != 11:
            raise ValueError("Invalid card number length")

        if len(self.insurant_number) != 11:
            raise ValueError("Invalid insurance number length")

        resp = requests.post(
            RFZO_URL,
            data={
                "zk": self.card_id,
                "lbo": self.insurant_number
            },
            timeout=(4, timeout),
        )

        resp.raise_for_status()

        match = re.search(
            r"оверена до:\s*<strong>(\d+\.\d+\.\d+\.)</strong>",
            resp.text
        )

        if not match:
            raise ValueError("RFZO response did not contain validity date")

        self.valid_until = match.group(1)

    # -------- RFZO HTML parsing --------

    @staticmethod
    def _parse_rfzo_valid_until(html: str) -> str:
        """
        Extract 'оверена до' date from RFZO HTML response.
        """

        match = re.search(
            r"оверена до:\s*<strong>(\d+\.\d+\.\d+\.)</strong>",
            html,
            re.IGNORECASE,
        )

        if not match:
            raise RfzoParseError("Could not extract validity date from RFZO response")

        return match.group(1)
