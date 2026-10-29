import json
import os

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "user_settings.json")

DEFAULT_SETTINGS = {
    "currency_symbol": "$",
    "currency_name": "USD ($)",
    "theme_name": "cosmo"
}

CURRENCY_OPTIONS = {
    "USD ($)": "$",
    "EUR (€)": "€",
    "GBP (£)": "£",
    "INR (₹)": "₹",
    "JPY (¥)": "¥",
    "CAD ($)": "CA$",
    "AUD ($)": "A$",
    "BRL (R$)": "R$"
}

def load_settings() -> dict:
    """Load user settings from JSON file, returning defaults if not found."""
    if os.path.exists(CONFIG_FILE_PATH):
        try:
            with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return {**DEFAULT_SETTINGS, **data}
        except Exception as e:
            print(f"Error loading settings: {e}")
    return DEFAULT_SETTINGS.copy()

def save_settings(settings: dict) -> bool:
    """Save user settings dict to JSON file."""
    try:
        with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False
