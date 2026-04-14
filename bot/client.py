import os
import time
import requests
from dotenv import load_dotenv
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from .logging_config import get_logger

logger = get_logger(__name__)

# Load environment variables
load_dotenv()

class MockBinanceWrapper:
    def futures_create_order(self, *args, **kwargs): pass
    def futures_account(self, *args, **kwargs): pass
    def futures_get_order(self, *args, **kwargs): pass

class BinanceClient:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")
        self.api_secret = os.getenv("API_SECRET")
        
        if not self.api_key or not self.api_secret:
            logger.warning("API_KEY or API_SECRET not found in .env. Operating in MOCK_MODE.")
            self.mock_mode = True
        else:
            self.mock_mode = False
        
        # Testnet URL
        self.base_url = "https://testnet.binancefuture.com"
        
        try:
            if not self.mock_mode:
                self.client = Client(
                    self.api_key, 
                    self.api_secret, 
                    testnet=True
                )
                # Make sure futures base url is set to testnet
                self.client.FUTURES_URL = self.base_url
                logger.info("BinanceClient initialized with testnet=True.")
            else:
                self.client = MockBinanceWrapper()
                logger.info("BinanceClient initialized in MOCK_MODE.")
        except Exception as e:
            logger.error(f"Failed to initialize BinanceClient: {str(e)}")
            raise

    def request_with_retry(self, method, *args, **kwargs):
        """Executes a binance-python client method with retry logic."""
        if self.mock_mode:
            method_name = method.__name__ if hasattr(method, '__name__') else str(method)
            logger.info(f"MOCK API Request: {method_name} | args={args} | kwargs={kwargs}")
            time.sleep(0.5)  # Simulate network logic
            status = "FILLED" if kwargs.get("type", "") == "MARKET" else "NEW"
            mock_resp = {
                "orderId": int(time.time() * 1000),
                "symbol": kwargs.get("symbol", "MOCK_BTCUSDT"),
                "side": kwargs.get("side", "BUY"),
                "type": kwargs.get("type", "MARKET"),
                "origQty": str(kwargs.get("quantity", "0.00")),
                "executedQty": str(kwargs.get("quantity", "0.00")),
                "price": str(kwargs.get("price", "94000.00")),
                "avgPrice": str(kwargs.get("price", "94000.00")),
                "status": status,
                "updateTime": int(time.time() * 1000)
            }
            logger.info(f"MOCK API Response Success: {method_name} | response={mock_resp}")
            return mock_resp

        max_retries = 3
        delay = 2
        
        # Log request
        method_name = method.__name__ if hasattr(method, '__name__') else str(method)
        logger.info(f"API Request: {method_name} | args={args} | kwargs={kwargs}")

        for attempt in range(1, max_retries + 1):
            try:
                response = method(*args, **kwargs)
                logger.info(f"API Response Success: {method_name} | response={response}")
                return response
            except requests.exceptions.ConnectionError as ce:
                logger.error(f"Network ConnectionError (attempt {attempt}/{max_retries}): {str(ce)}")
                if attempt < max_retries:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached. Failing request.")
                    raise
            except requests.exceptions.Timeout as te:
                logger.error(f"Network Timeout (attempt {attempt}/{max_retries}): {str(te)}")
                if attempt < max_retries:
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error("Max retries reached. Failing request.")
                    raise
            except BinanceOrderException as boe:
                logger.error(f"BinanceOrderException: code={boe.status_code} msg={boe.message}")
                raise
            except BinanceAPIException as bae:
                logger.error(f"BinanceAPIException: code={bae.status_code} msg={bae.message}")
                raise
            except Exception as e:
                logger.error(f"Unexpected Exception: {str(e)}")
                raise

    def test_connection(self) -> dict:
        """Tests the connection by fetching account information."""
        logger.info("Testing connection to Binance Futures Testnet...")
        if self.mock_mode:
            logger.info("MOCK Connection test successful.")
            return {
                "status": "success (mock mode)",
                "usdt_balance": "10000.00",
                "canTrade": True
            }

        try:
            # We use futures_account for futures endpoint
            account = self.request_with_retry(self.client.futures_account)
            
            # Find USDT balance
            usdt_balance = "0.00"
            for asset in account.get('assets', []):
                if asset.get('asset') == 'USDT':
                    usdt_balance = asset.get('availableBalance')
                    break
                    
            logger.info("Connection test successful.")
            return {
                "status": "success",
                "usdt_balance": usdt_balance,
                "canTrade": account.get('canTrade', False)
            }
        except Exception as e:
            logger.error("Connection test failed.")
            raise
