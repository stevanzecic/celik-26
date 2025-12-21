from core.tlv import parse_tlv
from core.encoding import decode_utf16le_date, decode_ascii_date


def _decode_utf16le(value: bytes) -> str:
    if not value:
        return ""
    try:
        return value.decode("utf-16le").strip("\x00")
    except Exception:
        return ""


# ---------------- DOCUMENT ----------------

def parse_medical_document(data: bytes, doc):
    fields = parse_tlv(data)

    doc.insurer_name = _decode_utf16le(fields.get(1553, b""))
    doc.insurer_id = fields.get(1554, b"").decode(errors="ignore")
    doc.card_id = fields.get(1555, b"").decode(errors="ignore")

    doc.date_of_issue = decode_ascii_date(fields.get(1557, b""))
    doc.date_of_expiry = decode_ascii_date(fields.get(1558, b""))

    doc.print_language = fields.get(1560, b"").decode(errors="ignore")


# ---------------- FIXED PERSONAL ----------------

def parse_medical_fixed_personal(data: bytes, doc):
    fields = parse_tlv(data)

    doc.last_name = _decode_utf16le(fields.get(1570, b""))
    doc.last_name_latin = _decode_utf16le(fields.get(1571, b""))
    doc.first_name = _decode_utf16le(fields.get(1572, b""))
    doc.first_name_latin = _decode_utf16le(fields.get(1573, b""))

    doc.date_of_birth = decode_ascii_date(fields.get(1574, b""))
    doc.insurant_number = fields.get(1569, b"").decode(errors="ignore")



# ---------------- VARIABLE PERSONAL ----------------

def parse_medical_variable_personal(data: bytes, doc):
    fields = parse_tlv(data)

    doc.valid_until = decode_utf16le_date(fields.get(1586, b""))
    doc.permanently_valid = fields.get(1587, b"") == b"1"


# ---------------- VARIABLE ADMIN ----------------

def parse_medical_variable_admin(data: bytes, doc):
    fields = parse_tlv(data)

    doc.parent_name = _decode_utf16le(fields.get(1601, b""))
    doc.gender = "M" if fields.get(1603) == b"01" else "F"
    doc.jmbg = fields.get(1604, b"").decode(errors="ignore")

    doc.street = _decode_utf16le(fields.get(1605, b""))
    doc.place = _decode_utf16le(fields.get(1608, b""))
    doc.municipality = _decode_utf16le(fields.get(1607, b""))
