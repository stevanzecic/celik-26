"""
MedicalDocument model for Serbian Medical Insurance Card.

- Holds data parsed directly from the card
- Provides explicit RFZO update on user action
- No UI logic
- No threading
"""

import re
from dataclasses import dataclass

RFZO_URL = "https://rfzo.rs/api_overa.php"
RFZO_REFERER = "https://rfzo.rs/"


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
    parent_name_latin: str = ""

    gender: str = ""
    jmbg: str = ""
    insurant_number: str = ""

    date_of_birth: str = ""
    date_of_issue: str = ""
    date_of_expiry: str = ""
    chip_serial_number: str = ""

    street: str = ""
    street_code: str = ""
    number: str = ""
    entrance: str = ""
    apartment: str = ""
    place: str = ""
    post_number: str = ""
    municipality: str = ""
    country: str = ""

    valid_until: str = ""
    permanently_valid: bool = False

    print_language: str = ""

    carrier_given_name: str = ""
    carrier_given_name_latin: str = ""
    carrier_family_name: str = ""
    carrier_family_name_latin: str = ""
    carrier_id_number: str = ""
    carrier_insurant_number: str = ""
    carrier_family_member: bool = False
    carrier_relationship: str = ""

    insurance_basis_rzzo: str = ""
    insurance_start_date: str = ""
    insurance_description: str = ""

    taxpayer_name: str = ""
    taxpayer_residence: str = ""
    taxpayer_number: str = ""
    taxpayer_id_number: str = ""
    taxpayer_activity_code: str = ""

    # -------- RFZO enriched data --------

    rfzo_valid_until: str | None = None
    rfzo_checked: bool = False

    # -------- Helpers --------

    def full_name_latin(self) -> str:
        return " ".join(
            value
            for value in (
                self.first_name_latin,
                self.parent_name_latin,
                self.last_name_latin,
            )
            if value
        )

    def full_address(self) -> str:
        street = " ".join(value for value in (self.street, self.number) if value)
        place = ", ".join(
            value for value in (self.place, self.municipality, self.country) if value
        )
        return ", ".join(value for value in (street, place) if value)

    # -------- RFZO UPDATE (MANUAL) --------

    def update_from_rfzo(self, timeout=8):
        if len(self.card_id) != 11:
            raise InvalidCardNumber("Invalid card number length")

        if len(self.insurant_number) != 11:
            raise InvalidInsurantNumber("Invalid insurance number length")

        # Keep the optional web dependency out of the offline card-reading path.
        import requests

        resp = requests.get(
            RFZO_URL,
            params={
                "kzo": self.card_id,
                "lbo": self.insurant_number,
            },
            # RFZO's public form calls this endpoint from its own site.  Send the
            # same essential request metadata; some deployments otherwise return
            # the web page instead of the API response.
            headers={
                "Accept": "application/json, text/plain, */*",
                "Referer": RFZO_REFERER,
                "User-Agent": "Mozilla/5.0",
            },
            timeout=(4, timeout),
        )

        resp.raise_for_status()

        try:
            payload = resp.json()
        except (TypeError, ValueError) as exc:
            content_type = str(resp.headers.get("Content-Type", "")).lower()
            if "html" in content_type:
                raise RfzoParseError(
                    "RFZO verification service returned a web page instead of "
                    "verification data. Please try again later."
                ) from exc
            raise RfzoParseError("RFZO returned an invalid JSON response") from exc

        value = self._parse_rfzo_payload(payload)
        self.rfzo_valid_until = value
        self.rfzo_checked = True
        self.valid_until = value
        return value

    # -------- RFZO JSON parsing --------

    @staticmethod
    def _normalize_rfzo_date(value) -> str:
        """Validate and normalize the date returned by the RFZO API."""
        match = re.fullmatch(
            r"\s*(\d{1,2})\.(\d{1,2})\.(\d{4})\.?\s*",
            str(value or ""),
        )
        if not match:
            raise RfzoParseError("RFZO response did not contain a validity date")

        day, month, year = match.groups()
        return f"{int(day):02d}.{int(month):02d}.{year}."

    @classmethod
    def _parse_rfzo_payload(cls, payload) -> str:
        """Extract the validity date from the current RFZO JSON response."""
        if isinstance(payload, list):
            if not payload:
                raise RfzoParseError("RFZO did not return card data")
            payload = payload[0]

        if not isinstance(payload, dict):
            raise RfzoParseError("RFZO returned an unexpected response format")

        return cls._normalize_rfzo_date(payload.get("zk_overena_do"))
