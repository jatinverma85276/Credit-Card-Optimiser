CATEGORY_MAP = {
    "clothing": "online_shopping",
    "fashion": "online_shopping",
    "electronics": "online_shopping",
    "food": "dining",
    "restaurant": "dining",
    "travel": "travel"
}

def normalize_category(category: str) -> str:
    if not category:
        return "other"
    return CATEGORY_MAP.get(category.lower(), category.lower())
