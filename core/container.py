from core.tlv import parse_tlv

def unwrap_container(data: bytes) -> bytes:
    """
    Unwraps outer Gemalto container TLV.
    Assumes exactly one top-level tag.
    """
    outer = parse_tlv(data)
    if not outer:
        raise ValueError("Empty container")
    return next(iter(outer.values()))
