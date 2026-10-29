from datetime import datetime
from utils.config import load_settings

def get_current_currency_symbol() -> str:
    settings = load_settings()
    return settings.get("currency_symbol", "$")

def format_currency(amount: float, symbol: str = None) -> str:
    if symbol is None:
        symbol = get_current_currency_symbol()
    return f"{symbol}{amount:,.2f}"

def format_date_display(date_str: str) -> str:
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%b %d, %Y")
    except ValueError:
        return date_str
