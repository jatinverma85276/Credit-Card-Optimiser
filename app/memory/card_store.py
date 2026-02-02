from typing import Dict
from app.graph.schemas import CreditCard

CARD_STORE: Dict[str, CreditCard] = {}

def add_card(card: CreditCard):
    CARD_STORE[card.card_name] = card

def get_all_cards():
    return list(CARD_STORE.values())
