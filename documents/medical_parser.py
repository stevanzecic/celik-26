from core.tlv import parse_tlv
from core.encoding import decode_utf16le_date, decode_ascii_date, _decode_utf16le


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

    # --- Core ---
    doc.parent_name = _decode_utf16le(fields.get(1601, b""))
    doc.gender = "M" if fields.get(1603) == b"01" else "F"
    doc.jmbg = fields.get(1604, b"").decode(errors="ignore")

    doc.street = _decode_utf16le(fields.get(1605, b""))
    doc.place = _decode_utf16le(fields.get(1608, b""))
    doc.municipality = _decode_utf16le(fields.get(1607, b""))

    # --- Address details (optional) ---
    doc.number = _decode_utf16le(fields.get(1606, b""))
    doc.apartment = _decode_utf16le(fields.get(1609, b""))

    # --- Carrier (policy holder) ---
    doc.carrier_given_name = _decode_utf16le(fields.get(1610, b""))
    doc.carrier_given_name_latin = _decode_utf16le(fields.get(1611, b""))
    doc.carrier_family_name = _decode_utf16le(fields.get(1612, b""))
    doc.carrier_family_name_latin = _decode_utf16le(fields.get(1613, b""))

    doc.carrier_id_number = fields.get(1614, b"").decode(errors="ignore")
    doc.carrier_insurant_number = fields.get(1615, b"").decode(errors="ignore")

    doc.carrier_family_member = fields.get(1616, b"") == b"1"
    doc.carrier_relationship = _decode_utf16le(fields.get(1617, b""))

    # --- Insurance ---
    doc.insurance_basis_rzzo = _decode_utf16le(fields.get(1620, b""))
    doc.insurance_start_date = decode_ascii_date(fields.get(1621, b""))
    doc.insurance_description = _decode_utf16le(fields.get(1622, b""))

    # --- Taxpayer ---
    doc.taxpayer_name = _decode_utf16le(fields.get(1630, b""))
    doc.taxpayer_residence = _decode_utf16le(fields.get(1631, b""))
    doc.taxpayer_number = fields.get(1632, b"").decode(errors="ignore")
    doc.taxpayer_id_number = fields.get(1633, b"").decode(errors="ignore")
    doc.taxpayer_activity_code = fields.get(1634, b"").decode(errors="ignore")
