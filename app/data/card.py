from app.models.card import CreditCard, CashbackRule

CARDS = [
    CreditCard(
        card_id="axis_ace",
        card_name="Axis Ace",
        card_type="cashback",
        cashback_rules={
            "online_shopping": CashbackRule(
                category="online_shopping",
                percentage=2.0,
                monthly_cap=None
            )
        }
    ),
    CreditCard(
        card_id="hdfc_millennia",
        card_name="HDFC Millennia",
        card_type="cashback",
        cashback_rules={
            "online_shopping": CashbackRule(
                category="online_shopping",
                percentage=5.0,
                monthly_cap=1000
            )
        }
    )
]
