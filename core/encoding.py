from datetime import date


# ---------------- DATE FORMATTERS - ID CARD ----------------

def s(data: bytes) -> str:
    """
    Safe UTF-8 decode

    Parameters:
        data (bytes): Data to decode
    Returns:
        str: Decoded string
    """
    return data.decode("utf-8", "ignore").strip("\x00 \t\r\n")

def format_date_yyyymmdd(value: str) -> str:
    """
    Converts DDMMYYYY → YYYY-MM-DD
    Leaves value unchanged if length is unexpected.

    Parameters:
        value (str): Date value
    Returns:
        str: Formatted date
    """
    if len(value) == 8 and value.isdigit():
        return f"{value[4:8]}-{value[2:4]}-{value[0:2]}"
    return value

def format_date_ddmmyyyy(value: str) -> str:
    """
    Converts DDMMYYYY → DD.MM.YYYY.
    Leaves value unchanged if length is unexpected.

    Parameters:
        value (str): Date value
    Returns:
        str: Formatted date
    """
    if len(value) == 8 and value.isdigit():
        day = int(value[0:2])
        month = int(value[2:4])
        year = int(value[4:8])

        # 01.01.0001 is the card/service sentinel for an unavailable date.
        if year <= 1:
            return ""

        try:
            date(year, month, day)
        except ValueError:
            return ""

        return f"{day:02d}.{month:02d}.{year:04d}."
    return value

# ---------------- DATE FORMATTERS - MEDICAL CARD ----------------

def decode_utf16le_date(value: bytes) -> str:
    """
    Expects DDMMYYYY as UTF-16LE, returns DD.MM.YYYY.

    Parameters:
        value (bytes): Date value
    Returns:
        str: Formatted date (DD.MM.YYYY.) or empty string if failed
    """
    if not value:
        return ""

    decoded = _decode_utf16le(value)
    digits = "".join(char for char in decoded if char.isdigit())

    # Expected DDMMYYYY
    if len(digits) == 8 and digits.isdigit():
        return format_date_ddmmyyyy(digits)

    return ""

def decode_ascii_date(value: bytes) -> str:
    """
    Expects DDMMYYYY as ASCII, returns DD.MM.YYYY.

    Parameters:
        value (bytes): Date value
    Returns:
        str: Formatted date (DD.MM.YYYY.) or empty string if failed
    """
    try:
        s = value.decode("ascii").strip()
        if len(s) == 8 and s.isdigit():
            return format_date_ddmmyyyy(s)
    except UnicodeDecodeError:
        return ""
    return ""

def _decode_utf16le(value: bytes) -> str:
    """
    Expects UTF-16LE string, returns decoded string.

    Parameters:
        value (bytes): String value
    Returns:
        str: Decoded string
    """
    if not value:
        return ""
    try:
        encoding = "utf-16" if value.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-16le"
        return value.decode(encoding).strip("\ufeff\x00 \t\r\n")
    except (UnicodeDecodeError, ValueError):
        return ""
