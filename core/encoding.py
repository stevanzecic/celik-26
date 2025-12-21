# ---------------- DATE FORMATTERS - ID CARD ----------------

def s(data: bytes) -> str:
    """Safe UTF-8 decode"""
    return data.decode("utf-8", "ignore").strip()

def format_date_yyyymmdd(value: str) -> str:
    """
    Converts DDMMYYYY → YYYY-MM-DD
    Leaves value unchanged if length is unexpected.
    """
    if len(value) == 8 and value.isdigit():
        return f"{value[4:8]}-{value[2:4]}-{value[0:2]}"
    return value

def format_date_ddmmyyyy(value: str) -> str:
    """
    Converts DDMMYYYY → DD.MM.YYYY
    Leaves value unchanged if length is unexpected.
    """
    if len(value) == 8 and value.isdigit():
        return f"{value[0:2]}.{value[2:4]}.{value[4:8]}"
    return value

# ---------------- DATE FORMATTERS - MEDICAL CARD ----------------

def decode_utf16le_date(value: bytes) -> str:
    if not value:
        return ""

    # UTF-16LE digits: digit byte is ALWAYS the LOW byte
    digits = value[::2].decode("ascii", errors="ignore")

    # Expected DDMMYYYY
    if len(digits) == 8 and digits.isdigit():
        return f"{digits[4:8]}-{digits[2:4]}-{digits[0:2]}"

    return ""

def decode_ascii_date(value: bytes) -> str:
    """
    Expects DDMMYYYY as ASCII
    """
    try:
        s = value.decode("ascii").strip()
        if len(s) == 8:
            return f"{s[0:2]}.{s[2:4]}.{s[4:8]}"
    except Exception:
        pass
    return ""