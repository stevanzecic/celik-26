"""
ATR values for ID cards
"""

# ----------------------------
# Gemalto / Veridos ID cards
# ----------------------------

GEMALTO_ATRS = {
    bytes.fromhex("3B FF 94 00 00 81 31 80 43 80 31 80 65 B0 85 02 01 F3 12 0F FF 82 90 00 79"),
    bytes.fromhex("3B F9 96 00 00 80 31 FE 45 53 43 45 37 20 47 43 4E 33 5E"),
    bytes.fromhex("3B 9E 96 80 31 FE 45 53 43 45 20 38 2E 30 2D 43 31 56 30 0D 0A 6F"),
    bytes.fromhex("3B 9E 96 80 31 FE 45 53 43 45 20 38 2E 30 2D 43 32 56 30 0D 0A 6C"),
}

# ----------------------------
# Apollo ID cards
# ----------------------------

APOLLO_ATR = bytes.fromhex(
    "3B B9 18 00 81 31 FE 9E 80 73 FF 61 40 83 00 00 00 DF"
)
