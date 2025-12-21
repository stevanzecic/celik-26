def build_apdu(
    cla: int,
    ins: int,
    p1: int,
    p2: int,
    data: bytes = b"",
    le: int | None = None,
) -> list[int]:
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
    offset: 0–65535
    length: max 0xFF per APDU
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
