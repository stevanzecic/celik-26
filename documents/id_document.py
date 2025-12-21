"""
Serbian ID document class definition

Class: IdDocument
Class methods:
    full_name() - Get full name of the person (name + parent name + surname)
    address() - Get address of the person (street + house number + house letter + place + community)
"""
from dataclasses import dataclass
from typing import Optional
from PIL import Image


@dataclass
class IdDocument:
    # --- Document ---
    doc_reg_no: str = ""
    document_type: str = ""
    document_serial_number: str = ""
    issuing_date: str = ""
    expiry_date: str = ""
    issuing_authority: str = ""
    chip_serial_number: str = ""
    document_name: str = ""

    # --- Personal ---
    personal_number: str = ""      # JMBG
    surname: str = ""
    given_name: str = ""
    parent_given_name: str = ""
    sex: str = ""
    place_of_birth: str = ""
    community_of_birth: str = ""
    state_of_birth: str = ""
    state_of_birth_code: str = ""
    date_of_birth: str = ""
    nationality_full: str = ""
    purpose_of_stay: str = ""
    e_note: str = ""

    # --- Residence ---
    state: str = ""
    community: str = ""
    place: str = ""
    street: str = ""
    house_number: str = ""
    house_letter: str = ""
    entrance: str = ""
    floor: str = ""
    apartment_number: str = ""
    address_date: str = ""
    address_label: str = ""

    # --- Portrait ---
    portrait: Optional[Image.Image] = None

    def full_name(self) -> str:
        """
        Get full name of the person (name + parent name + surname).

        Parameters:
            None
        Returns:
            str: Full name
        """
        return " ".join(p for p in [self.given_name, self.parent_given_name, self.surname] if p)

    def address(self) -> str:
        """
        Get address of the person (street + house number + house letter + place + community).

        Parameters:
            None
        Returns:
            str: Address
        """
        parts = [
            self.street,
            self.house_number + self.house_letter,
            self.place,
            self.community,
        ]
        return ", ".join(p for p in parts if p)

    # def __repr__(self):
    #     return (
    #         "IdDocument(\n"
    #         f"  Name: {self.full_name()}\n"
    #         f"  JMBG: {self.personal_number}\n"
    #         f"  Date of birth: {self.date_of_birth}\n"
    #         f"  Sex: {self.sex}\n"
    #         f"  Address: {self.address()}\n"
    #         f"  Issuer: {self.issuing_authority}\n"
    #         ")"
    #     )
