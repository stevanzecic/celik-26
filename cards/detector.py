"""
Detect card type by ATR, read card data, format card data, and return dictionary with card type and data.
"""
from cards.id.gemalto import GemaltoIDCard
from cards.id.apollo import ApolloIDCard
from cards.id.atr import GEMALTO_ATRS, APOLLO_ATR
from cards.medical.medical import MEDICAL_ATRS, MedicalCard


def detect_card(pcsc):
    atr = pcsc.atr()

    # Apollo has a unique, fixed ATR and does not require application probing.
    if atr == APOLLO_ATR:
        return {"type": "ID", "data": ApolloIDCard(pcsc).read_and_retrieve_document()}

    # Older medical cards also have unique ATR values.
    if atr in MEDICAL_ATRS:
        return {"type": "MED", "data": MedicalCard(pcsc).read_and_retrieve_document()}

    # Newer medical cards share ATR values with Gemalto/Veridos ID cards, so
    # even a known ATR must be disambiguated by selecting the application.
    for card_type, card_class in (
        ("ID", GemaltoIDCard),
        ("MED", MedicalCard),
    ):
        card = card_class(pcsc)
        if card.test():
            return {
                "type": card_type,
                "data": card.read_and_retrieve_document(),
            }

    raise RuntimeError(f"Unknown card type (ATR: {atr.hex(' ').upper()})")
