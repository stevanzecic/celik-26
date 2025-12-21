from core.pcsc import connect_first_card
from cards.detector import detect_card

def read_card():
    """
    Detect card and read data. Returns dictionary with card type and data.
    card_data = {
        "type": ,
        "data": None
    }
    Parameters:
        None
    Returns:
        dict:    {"type": "ID" | "MED", "data": <CARD DATA>}
    """
    pcsc = connect_first_card()
    card = detect_card(pcsc)
    return card

def main():
    pcsc = connect_first_card()
    read_card = detect_card(pcsc)
    card = read_card["data"]

    print("# # #  TEST 1  # # #")

    print("Detected card:", type(card).__name__)
    print("ATR:", card.atr)

    print("# # #  TEST 2  # # #")

    print("Detected card:", type(card).__name__)
    print("ATR:", card.atr)

    card.read()

    print("# # #  TEST 3  # # #")

    doc = card.get_document()
    print(doc)


if __name__ == "__main__":
    main()
