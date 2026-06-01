import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logging(log_filename="trading_bot.log", log_level=logging.INFO):
    """
    Sets up application logging. Logs are written to a file and, optionally,
    important errors are logged.
    """
    # Ensure logs directory or path is fine. We will write to the root of the trading_bot directory
    # or where the bot is run from.
    log_format = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # File Handler - with rotating logic to prevent infinite growth
    file_handler = RotatingFileHandler(
        log_filename,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding="utf-8"
    )
    file_handler.setFormatter(log_format)
    file_handler.setLevel(log_level)

    # Root Logger Setup
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove any existing handlers to prevent double logs
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    root_logger.addHandler(file_handler)

    # Suppress verbose third-party logs (like urllib3, requests, websockets)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    logging.getLogger("binance").setLevel(logging.WARNING)

    # Create a specific logger for the bot
    logger = logging.getLogger("trading_bot")
    logger.info("Logging successfully initialized. Writing logs to %s", os.path.abspath(log_filename))
    return logger
