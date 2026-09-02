"""
Serbian ID TLV format parsing - extracting specific data chunks from Serbian ID card data

Functions:
    parse_id_document(data: bytes, doc: IdDocument) - Parse Serbian ID document data
    parse_id_personal(data: bytes, doc: IdDocument) - Parse Serbian ID personal data
    parse_id_residence(data: bytes, doc: IdDocument) - Parse Serbian ID residence data
    parse_id_portrait(data: bytes) - Parse Serbian ID portrait data
"""
from PIL import Image
import io

from core.tlv import parse_tlv
from core.encoding import s, format_date_ddmmyyyy



def parse_id_document(data: bytes, doc):
    """
    Parse Serbian ID document data.

    Parameters:
        data (bytes): Document data
        doc (IdDocument): Document object
    Returns:
        None
    """
    f = parse_tlv(data)

    doc.doc_reg_no = s(f.get(1546, b""))
    doc.document_type = s(f.get(1547, b""))
    doc.document_serial_number = s(f.get(1548, b""))
    doc.issuing_date = format_date_ddmmyyyy(s(f.get(1549, b"")))
    doc.expiry_date = format_date_ddmmyyyy(s(f.get(1550, b"")))
    doc.issuing_authority = s(f.get(1551, b""))
    doc.chip_serial_number = s(f.get(1681, b""))
    doc.document_name = s(f.get(1682, b""))


def parse_id_personal(data: bytes, doc):
    """
    Parse Serbian ID personal data.

    Parameters:
        data (bytes): Personal data
        doc (IdDocument): Document object
    Returns:
        None
    """
    f = parse_tlv(data)

    doc.personal_number = s(f.get(1558, b""))
    doc.surname = s(f.get(1559, b""))
    doc.given_name = s(f.get(1560, b""))
    doc.parent_given_name = s(f.get(1561, b""))
    doc.sex = s(f.get(1562, b""))
    doc.place_of_birth = s(f.get(1563, b""))
    doc.community_of_birth = s(f.get(1564, b""))
    doc.state_of_birth = s(f.get(1565, b""))
    doc.date_of_birth = format_date_ddmmyyyy(s(f.get(1566, b"")))
    doc.state_of_birth_code = s(f.get(1567, b""))
    doc.nationality_full = s(f.get(1583, b""))
    doc.purpose_of_stay = s(f.get(1683, b""))
    if not doc.purpose_of_stay:
        doc.purpose_of_stay = s(f.get(1582, b""))
    doc.e_note = s(f.get(1684, b""))


def parse_id_residence(data: bytes, doc):
    """
    Parse Serbian ID residence data.

    Parameters:
        data (bytes): Residence data
        doc (IdDocument): Document object
    Returns:
        None
    """
    f = parse_tlv(data)

    doc.state = s(f.get(1568, b""))
    doc.community = s(f.get(1569, b""))
    doc.place = s(f.get(1570, b""))
    doc.street = s(f.get(1571, b""))
    doc.house_number = s(f.get(1572, b""))
    doc.house_letter = s(f.get(1573, b""))
    doc.entrance = s(f.get(1574, b""))
    doc.floor = s(f.get(1575, b""))
    doc.apartment_number = s(f.get(1578, b""))
    doc.address_date = format_date_ddmmyyyy(s(f.get(1580, b"")))
    doc.address_label = s(f.get(1581, b""))

def parse_id_portrait(data: bytes):
    """
    Parse Serbian ID portrait data.

    Parameters:
        data (bytes): Portrait data
    Returns:
        Image.Image | None: Portrait image or None if failed
    """
    if not data or len(data) <= 4:
        return None

    jpeg = data[4:]

    try:
        return Image.open(io.BytesIO(jpeg))
    except Exception:
        return None
