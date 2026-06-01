import logging
from binance.client import Client
from binance.exceptions import BinanceAPIException

logger = logging.getLogger("trading_bot")

class BinanceTestnetClient:
    """
    Wrapper around the python-binance Client configured specifically 
    for the Binance Futures Testnet (USDT-M).
    """
    def __init__(self, api_key: str, api_secret: str):
        if not api_key or not api_secret:
            logger.error("Binance API Key or Secret is missing.")
            raise ValueError("API Key and Secret must be provided to initialize the Binance Client.")
            
        logger.info("Initializing Binance Futures Testnet Client...")
        # Initialize client with testnet=True to automatically route to testnet endpoints.
        self.client = Client(api_key, api_secret, testnet=True)
        # Note: python-binance does not automatically override the Futures URL for testnet.
        # We explicitly set the Futures URL to the Testnet endpoint.
        self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
        
        # Synchronize local time with Binance Server time to prevent Code -1021 errors
        try:
            import time
            server_time = self.client.get_server_time()
            local_time = int(time.time() * 1000)
            self.client.timestamp_offset = server_time['serverTime'] - local_time
            logger.info("Time synchronization complete. Offset: %s ms", self.client.timestamp_offset)
        except Exception as e:
            logger.warning("Could not synchronize time with Binance: %s. Using default system time.", str(e))
        
    def ping(self) -> bool:
        """
        Pings the Binance Futures server to check connection status.
        """
        try:
            logger.info("Pinging Binance Futures Testnet server...")
            # For Futures USDT-M, we use client.futures_ping()
            self.client.futures_ping()
            logger.info("Ping successful. Connected to Binance Futures Testnet.")
            return True
        except BinanceAPIException as e:
            logger.error("Binance API Exception during ping: Code %s - %s", e.code, e.message)
            raise
        except Exception as e:
            logger.error("Unexpected error during ping: %s", str(e))
            raise
            
    def get_account_balance(self) -> float:
        """
        Fetches the total account balance for USDT from the Futures Testnet account.
        """
        try:
            logger.info("Fetching futures account details...")
            account_info = self.client.futures_account()
            
            # Find the USDT balance asset
            for asset in account_info.get("assets", []):
                if asset.get("asset") == "USDT":
                    balance = float(asset.get("walletBalance", 0.0))
                    logger.info("USDT Futures Wallet Balance: %s", balance)
                    return balance
            return 0.0
        except BinanceAPIException as e:
            logger.error("Failed to fetch account balance: %s", e.message)
            raise
        except Exception as e:
            logger.error("Unexpected error fetching account balance: %s", str(e))
            raise
