"""
APDU (Application Protocol Data Unit) helpers - communication messages format

Functions:
    build_apdu(cla, ins, p1, p2, data, le) - Build APDU
    read_binary(pcsc, offset, length) - Read binary data from the card
"""

def build_apdu(
    cla: int,
    ins: int,
    p1: int,
    p2: int,
    data: bytes = b"",
    le: int | None = None,
) -> list[int]:
    """
    Build APDU (ISO 7816-4)

    Parameters:
        cla (int): CLA byte
        ins (int): INS byte
        p1 (int): P1 byte
        p2 (int): P2 byte
        data (bytes): Data bytes
        le (int | None): Expected response length
    Returns:
        list[int]: APDU bytes
    """
    for name, value in (("cla", cla), ("ins", ins), ("p1", p1), ("p2", p2)):
        if not isinstance(value, int) or not 0 <= value <= 0xFF:
            raise ValueError(f"{name} must be an integer between 0 and 255")

    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    if len(data) > 0xFF:
        raise ValueError("Only short APDUs (up to 255 data bytes) are supported")
    if le is not None and (not isinstance(le, int) or not 1 <= le <= 0x100):
        raise ValueError("le must be between 1 and 256")

    apdu = [cla, ins, p1, p2]

    if data:
        apdu.append(len(data))
        apdu.extend(data)

    if le is not None:
        # In a short APDU, Le=0 encodes an expected length of 256 bytes.
        apdu.append(0 if le == 0x100 else le)

    return apdu

def read_binary(pcsc, offset: int, length: int) -> bytes:
    """
    READ BINARY (ISO 7816-4)

    Parameters:
        pcsc (PcscCard): Card connection
        offset (int): Offset (0-65535)
        length (int): Length (max 0xFF per APDU)
    Returns:
        bytes: Binary data
    """
    if not isinstance(offset, int) or not 0 <= offset < 0xFFFF:
        raise ValueError("offset must be between 0 and 65534")
    if not isinstance(length, int) or length < 0:
        raise ValueError("length must be a non-negative integer")
    if length == 0:
        return b""

    p1 = (offset >> 8) & 0xFF
    p2 = offset & 0xFF

    apdu = build_apdu(0x00, 0xB0, p1, p2, b"", min(length, 0xFF))
    rsp = pcsc.transmit(apdu)

    if len(rsp) < 2:
        raise RuntimeError("Invalid READ BINARY response")

    sw = rsp[-2:]
    if sw != b"\x90\x00":
        raise RuntimeError(f"READ BINARY failed: {sw.hex()}")

    return rsp[:-2]
