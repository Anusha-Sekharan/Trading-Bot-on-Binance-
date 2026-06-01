import logging
from binance.exceptions import BinanceAPIException
from bot.client import BinanceTestnetClient

logger = logging.getLogger("trading_bot")

def place_futures_order(
    client: BinanceTestnetClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float | None = None,
    time_in_force: str = "GTC"
) -> dict:
    """
    Places an order on the Binance Futures Testnet (USDT-M).
    
    :param client: An instance of BinanceTestnetClient.
    :param symbol: Trading symbol, e.g., 'BTCUSDT'.
    :param side: 'BUY' or 'SELL'.
    :param order_type: 'MARKET' or 'LIMIT'.
    :param quantity: The quantity to trade.
    :param price: The price at which to place the order (required for LIMIT).
    :param time_in_force: The Time In Force strategy (default 'GTC' for LIMIT).
    :return: Dictionary containing status, order details, or error message.
    """
    logger.info(
        "Preparing order execution request: Symbol=%s, Side=%s, Type=%s, Quantity=%s, Price=%s",
        symbol, side, order_type, quantity, price
    )
    
    # Prepare the payload for python-binance futures_create_order
    # We must format parameters correctly (e.g. avoiding sending price for MARKET orders)
    params = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity
    }
    
    if order_type == "LIMIT":
        params["price"] = price
        params["timeInForce"] = time_in_force

    logger.info("Sending order request payload to Binance Futures Testnet API: %s", params)
    
    try:
        # Call the underlying python-binance client's futures_create_order
        response = client.client.futures_create_order(**params)
        
        logger.info("Order placed successfully. Received API response: %s", response)
        
        # Parse the standard fields expected by the CLI / user
        order_id = response.get("orderId")
        status = response.get("status")
        executed_qty = response.get("executedQty", 0.0)
        avg_price = response.get("avgPrice")
        
        # If avgPrice isn't directly returned or is 0, try to check if there are fills
        if (not avg_price or float(avg_price) == 0.0) and "fills" in response:
            fills = response["fills"]
            if fills:
                total_qty = sum(float(f.get("qty", 0)) for f in fills)
                if total_qty > 0:
                    total_cost = sum(float(f.get("price", 0)) * float(f.get("qty", 0)) for f in fills)
                    avg_price = total_cost / total_qty
                    
        return {
            "success": True,
            "order_id": order_id,
            "status": status,
            "executed_qty": executed_qty,
            "avg_price": avg_price if avg_price else "N/A",
            "raw_response": response
        }
        
    except BinanceAPIException as e:
        logger.error(
            "Binance API Exception occurred while placing order: Code=%s | Message=%s",
            e.code, e.message
        )
        return {
            "success": False,
            "error_type": "BinanceAPIException",
            "code": e.code,
            "message": e.message
        }
    except Exception as e:
        logger.exception("Unexpected exception occurred while placing order: %s", str(e))
        return {
            "success": False,
            "error_type": "SystemError",
            "message": str(e)
        }
