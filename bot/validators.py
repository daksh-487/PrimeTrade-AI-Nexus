from typing import Optional
from .logging_config import get_logger

logger = get_logger(__name__)

def validate_symbol(symbol: str) -> str:
    if not symbol or not isinstance(symbol, str):
        raise ValueError("Symbol must be a non-empty string.")
    
    symbol = symbol.upper().strip()
    
    if not symbol.endswith("USDT"):
        raise ValueError(f"Invalid symbol '{symbol}'. Symbol must end with 'USDT' (e.g., BTCUSDT).")
    
    check_prefix = symbol[:-4]
    if not check_prefix.isalpha():
        raise ValueError(f"Invalid symbol '{symbol}'. Base asset must be alphabetic (e.g., BTC, ETH).")
    
    logger.debug(f"Validated symbol: {symbol}")
    return symbol

def validate_side(side: str) -> str:
    if not side or not isinstance(side, str):
        raise ValueError("Side must be a string.")
        
    side = side.upper().strip()
    if side not in ("BUY", "SELL"):
        raise ValueError(f"Invalid side '{side}'. Side must be either BUY or SELL.")
        
    logger.debug(f"Validated side: {side}")
    return side

def validate_order_type(order_type: str) -> str:
    if not order_type or not isinstance(order_type, str):
        raise ValueError("Order type must be a string.")
        
    order_type = order_type.upper().strip()
    valid_types = ("MARKET", "LIMIT", "STOP_LIMIT")
    if order_type not in valid_types:
        raise ValueError(f"Invalid order type '{order_type}'. Must be one of {', '.join(valid_types)}.")
        
    logger.debug(f"Validated order type: {order_type}")
    return order_type

def validate_quantity(quantity: str) -> float:
    try:
        qty_float = float(quantity)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid quantity '{quantity}'. Must be a valid number.")
        
    if qty_float <= 0:
        raise ValueError(f"Invalid quantity {qty_float}. Must be greater than 0.")
        
    logger.debug(f"Validated quantity: {qty_float}")
    return qty_float

def validate_price(price: Optional[str], order_type: str) -> Optional[float]:
    if order_type == "MARKET":
        if price is not None:
             logger.warning("Price provided for MARKET order. It will be ignored.")
        return None
        
    if price is None:
        raise ValueError(f"Price is required for {order_type} orders.")
        
    try:
        price_float = float(price)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid price '{price}'. Must be a valid number.")
        
    if price_float <= 0:
        raise ValueError(f"Invalid price {price_float}. Must be greater than 0.")
        
    logger.debug(f"Validated price: {price_float}")
    return price_float

def validate_stop_price(stop_price: Optional[str], order_type: str) -> Optional[float]:
    if order_type != "STOP_LIMIT":
        if stop_price is not None:
             logger.warning(f"Stop price provided for {order_type} order. It will be ignored.")
        return None
        
    if stop_price is None:
        raise ValueError("Stop price is required for STOP_LIMIT orders.")
        
    try:
        stop_float = float(stop_price)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid stop price '{stop_price}'. Must be a valid number.")
        
    if stop_float <= 0:
        raise ValueError(f"Invalid stop price {stop_float}. Must be greater than 0.")
        
    logger.debug(f"Validated stop price: {stop_float}")
    return stop_float
