"""
Serbian ID / Medical / Vehicle TLV format parsing

Functions:
    parse_tlv(data: bytes) - Parse TLV data
    assign_field(fields: dict, tag: int, obj, attr: str) - Assign field value to the object
    assign_bool_field(fields: dict, tag: int, obj, attr: str) - Assign boolean field value to the object
"""

# ------------------------------------------------------------------
# Parsing
# ------------------------------------------------------------------
def parse_tlv(data: bytes) -> dict[int, bytes]:
    """
    Serbian ID / Medical / Vehicle TLV format:

    TAG    : uint16 (little endian)
    LENGTH : uint16 (little endian)
    VALUE  : LENGTH bytes

    Parameters:
        data (bytes): TLV data
    Returns:
        dict[int, bytes]: Parsed TLV data
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    if not data:
        raise ValueError("TLV data is empty")

    pos = 0
    n = len(data)
    result = {}

    while pos < n:
        if pos + 4 > n:
            raise ValueError(f"Truncated TLV header at offset {pos}")

        tag = int.from_bytes(data[pos:pos+2], "little")
        length = int.from_bytes(data[pos+2:pos+4], "little")
        pos += 4

        if pos + length > n:
            raise ValueError(
                f"Truncated TLV value for tag {tag}: expected {length} bytes"
            )

        value = data[pos:pos+length]
        pos += length

        result[tag] = value

    return result


# ------------------------------------------------------------------
# Helpers
# ------------------------------------------------------------------

def assign_field(fields: dict, tag: int, obj, attr: str):
    """
    Assign field value to the object.

    Parameters:
        fields (dict): TLV data
        tag (int): Tag
        obj (object): Object to assign value to
        attr (str): Attribute name
    Returns:
        None
    """
    value = fields.get(tag)
    if value is None:
        return

    if isinstance(value, bytes):
        try:
            value = value.decode("utf-8")
        except Exception:
            value = value.decode(errors="ignore")

    setattr(obj, attr, value)


def assign_bool_field(fields: dict, tag: int, obj, attr: str):
    """
    Assign boolean field value to the object.

    Parameters:
        fields (dict): TLV data
        tag (int): Tag
        obj (object): Object to assign value to
        attr (str): Attribute name
    Returns:
        None
    """
    value = fields.get(tag)

    if not value:
        setattr(obj, attr, False)
        return

    if isinstance(value, bytes):
        value = value.decode(errors="ignore")

    setattr(obj, attr, value == "01")
