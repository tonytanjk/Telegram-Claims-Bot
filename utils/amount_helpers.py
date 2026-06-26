"""Helper functions for consistent amount handling throughout the bot."""

def clean_amount(amount_str: str) -> float:
    """Clean and convert amount string to float."""
    # Remove currency symbols, spaces, and commas
    cleaned = amount_str.strip().replace('$', '').replace(',', '').strip()
    return float(cleaned)

def format_amount_for_display(amount: float) -> str:
    """Format amount for display with currency symbol."""
    return "${:.2f}".format(amount)

def format_amount_for_sheet(amount: float) -> float:
    """Format amount for Google Sheet (as pure number)."""
    return float("{:.2f}".format(amount))
