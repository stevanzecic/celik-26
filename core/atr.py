"""
ATR (Answer To Reset) class definition
"""
class Atr(bytes):
    def __str__(self):
        return " ".join(f"{b:02X}" for b in self)
