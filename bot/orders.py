from typing import Dict, Any, Optional
from .client import BinanceClient
from .logging_config import get_logger

logger = get_logger(__name__)

class OrderManager:
    def __init__(self, client: BinanceClient):
        self.client = client

    def place_market_order(self, symbol: str, side: str, quantity: float) -> dict:
        kwargs = {
            "symbol": symbol,
            "side": side,
            "type": "MARKET",
            "quantity": quantity
        }
        logger.info(f"Preparing MARKET order: {kwargs}")
        response = self.client.request_with_retry(
            self.client.client.futures_create_order,
            **kwargs
        )
        return self._format_response(response)

    def place_limit_order(self, symbol: str, side: str, quantity: float, price: float) -> dict:
        kwargs = {
            "symbol": symbol,
            "side": side,
            "type": "LIMIT",
            "timeInForce": "GTC",
            "quantity": quantity,
            "price": price
        }
        logger.info(f"Preparing LIMIT order: {kwargs}")
        response = self.client.request_with_retry(
            self.client.client.futures_create_order,
            **kwargs
        )
        return self._format_response(response)

    def place_stop_limit_order(self, symbol: str, side: str, quantity: float, price: float, stop_price: float) -> dict:
        kwargs = {
            "symbol": symbol,
            "side": side,
            "type": "STOP",
            "timeInForce": "GTC",
            "quantity": quantity,
            "price": price,
            "stopPrice": stop_price
        }
        logger.info(f"Preparing STOP_LIMIT order: {kwargs}")
        response = self.client.request_with_retry(
            self.client.client.futures_create_order,
            **kwargs
        )
        return self._format_response(response)

    def get_order_status(self, symbol: str, order_id: int) -> dict:
        kwargs = {
            "symbol": symbol,
            "orderId": order_id
        }
        logger.info(f"Fetching order status: {kwargs}")
        response = self.client.request_with_retry(
            self.client.client.futures_get_order,
            **kwargs
        )
        return self._format_response(response)

    def _format_response(self, response: dict) -> dict:
        """Extracts key fields from the raw binance response dict."""
        return {
            "orderId": response.get("orderId"),
            "symbol": response.get("symbol"),
            "side": response.get("side"),
            "type": response.get("type"),
            "origQty": response.get("origQty"),
            "executedQty": response.get("executedQty"),
            "avgPrice": response.get("avgPrice") or response.get("price"),
            "status": response.get("status"),
            "timestamp": response.get("updateTime") or response.get("time")
        }

    def format_order_response(self, response: dict) -> str:
        """Returns a pretty human-readable summary of the order."""
        summary = (
            f"Order ID     : {response.get('orderId')}\n"
            f"Symbol       : {response.get('symbol')}\n"
            f"Side         : {response.get('side')}\n"
            f"Type         : {response.get('type')}\n"
            f"Quantity     : {response.get('origQty')}\n"
            f"Executed Qty : {response.get('executedQty')}\n"
            f"Average Price: {response.get('avgPrice')}\n"
            f"Status       : {response.get('status')}\n"
            f"Timestamp    : {response.get('timestamp')}"
        )
        return summary
