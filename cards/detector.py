"""
Detect card type by ATR, read card data, format card data, and return dictionary with card type and data.
"""
from cards.id.gemalto import GemaltoIDCard
from cards.id.apollo import ApolloIDCard
from cards.id.atr import GEMALTO_ATRS, APOLLO_ATR
from cards.medical.medical import MedicalCard


def detect_card(pcsc):
    atr = pcsc.atr()

    # 1️⃣ Exact ATR match
    if atr == APOLLO_ATR:
        return {"type": "ID", "data": ApolloIDCard(pcsc).read_and_retrieve_document()}

    if atr in GEMALTO_ATRS:
        return {"type": "ID", "data": GemaltoIDCard(pcsc).read_and_retrieve_document()}

    # 2️⃣ Fallback probing - ID cards first
    card = GemaltoIDCard(pcsc)
    if card.test():
        return {"type": "ID", "data": card.read_and_retrieve_document()}

    card = ApolloIDCard(pcsc)
    if card.test():
        return {"type": "ID", "data": card.read_and_retrieve_document()}

    # 3️⃣ Medical card detection
    card = MedicalCard(pcsc)
    if card.test():
        return {"type": "MED", "data": card.read_and_retrieve_document()}

    raise RuntimeError("Unknown card type")
