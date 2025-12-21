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
    apdu = [cla, ins, p1, p2]

    if data:
        apdu.append(len(data))
        apdu.extend(data)

    if le is not None:
        apdu.append(le)

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
