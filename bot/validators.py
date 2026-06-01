import re

class ValidationError(Exception):
    """Custom exception raised for CLI input validation failures."""
    pass

def validate_symbol(symbol: str) -> str:
    """
    Validates a trading symbol (e.g. BTCUSDT, ETHUSDT).
    Must be alphanumeric, uppercase, and follow a general pattern.
    """
    if not symbol:
        raise ValidationError("Symbol is required and cannot be empty.")
    
    clean_symbol = symbol.strip().upper()
    
    # Binance symbols are alphanumeric (e.g., BTCUSDT, 1000SHIBUSDT)
    # Typically 3 to 12 characters
    if not re.match(r"^[A-Z0-9]{3,15}$", clean_symbol):
        raise ValidationError(
            f"Invalid symbol format: '{symbol}'. "
            "Symbol must be alphanumeric and 3-15 characters long (e.g., BTCUSDT)."
        )
        
    return clean_symbol

def validate_side(side: str) -> str:
    """
    Validates the order side. Must be BUY or SELL.
    """
    if not side:
        raise ValidationError("Side is required.")
        
    clean_side = side.strip().upper()
    if clean_side not in ("BUY", "SELL"):
        raise ValidationError(f"Invalid side: '{side}'. Must be either 'BUY' or 'SELL'.")
        
    return clean_side

def validate_order_type(order_type: str) -> str:
    """
    Validates the order type. Must be MARKET or LIMIT.
    """
    if not order_type:
        raise ValidationError("Order type is required.")
        
    clean_type = order_type.strip().upper()
    if clean_type not in ("MARKET", "LIMIT"):
        raise ValidationError(f"Invalid order type: '{order_type}'. Must be either 'MARKET' or 'LIMIT'.")
        
    return clean_type

def validate_quantity(quantity: str) -> float:
    """
    Validates the quantity. Must be a positive number.
    """
    if not quantity:
        raise ValidationError("Quantity is required.")
        
    try:
        qty_val = float(quantity)
    except ValueError:
        raise ValidationError(f"Invalid quantity: '{quantity}'. Must be a valid number.")
        
    if qty_val <= 0:
        raise ValidationError(f"Quantity must be greater than zero. Provided: {qty_val}")
        
    return qty_val

def validate_price(price: str, order_type: str) -> float | None:
    """
    Validates the price.
    - Required for LIMIT orders, and must be a positive number.
    - Ignored/not allowed for MARKET orders.
    """
    order_type_upper = order_type.strip().upper()
    
    if order_type_upper == "LIMIT":
        if not price:
            raise ValidationError("Price is required for LIMIT orders.")
        try:
            price_val = float(price)
        except ValueError:
            raise ValidationError(f"Invalid price: '{price}'. Must be a valid number.")
            
        if price_val <= 0:
            raise ValidationError(f"Price must be greater than zero. Provided: {price_val}")
            
        return price_val
        
    elif order_type_upper == "MARKET":
        if price is not None and price != "":
            # Warn or raise validation error if a price is passed for market
            raise ValidationError("Price cannot be specified for MARKET orders.")
        return None
        
    return None

def validate_all(symbol: str, side: str, order_type: str, quantity: str, price: str | None = None) -> dict:
    """
    Runs all validators and returns a dictionary of validated parameters.
    """
    valid_symbol = validate_symbol(symbol)
    valid_side = validate_side(side)
    valid_type = validate_order_type(order_type)
    valid_qty = validate_quantity(quantity)
    valid_price = validate_price(price, valid_type)
    
    return {
        "symbol": valid_symbol,
        "side": valid_side,
        "type": valid_type,
        "quantity": valid_qty,
        "price": valid_price
    }
