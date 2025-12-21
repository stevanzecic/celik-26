def parse_tlv(data: bytes) -> dict[int, bytes]:
    """
    Serbian ID / Medical / Vehicle TLV format:

    TAG    : uint16 (little endian)
    LENGTH : uint16 (little endian)
    VALUE  : LENGTH bytes
    """
    pos = 0
    n = len(data)
    result = {}

    while pos + 4 <= n:
        tag = int.from_bytes(data[pos:pos+2], "little")
        length = int.from_bytes(data[pos+2:pos+4], "little")
        pos += 4

        if pos + length > n:
            break

        value = data[pos:pos+length]
        pos += length

        result[tag] = value

    return result


# ------------------------------------------------------------------
# Helpers equivalent to tlv.AssignField / AssignBoolField in Go
# ------------------------------------------------------------------

def assign_field(fields: dict, tag: int, obj, attr: str):
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
    value = fields.get(tag)

    if not value:
        setattr(obj, attr, False)
        return

    if isinstance(value, bytes):
        value = value.decode(errors="ignore")

    setattr(obj, attr, value == "01")
