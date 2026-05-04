from datetime import datetime

def format_currency(value):
    """Formatea un número como moneda Soles (S/)."""
    return f"S/ {value:,.2f}"

def format_date(date_obj):
    """Convierte un objeto fecha a string legible."""
    if isinstance(date_obj, datetime):
        return date_obj.strftime("%d/%m/%Y %H:%M")
    return str(date_obj)

def validate_positive_number(value):
    """Valida que una cantidad sea mayor o igual a cero."""
    try:
        return float(value) >= 0
    except:
        return False