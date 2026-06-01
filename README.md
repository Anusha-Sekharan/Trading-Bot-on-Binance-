# Simplified Binance Futures Testnet Trading Bot (USDT-M)

A clean, modular, and robust Python command-line utility for executing Market and Limit orders on the Binance Futures Testnet (USDT-M). It features comprehensive parameters validation, extensive file-based rotating logging, professional CLI aesthetics using `rich`, and complete exception handling.

---

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py        # Binance API client wrapper configured for Testnet
    orders.py        # Order placement and raw API communication logic
    validators.py    # Robust parameter validation (Symbol, Side, Type, Qty, Price)
    logging_config.py# Rotating file logger setup (trading_bot.log)
  cli.py             # Main CLI entrypoint with styled console interface
  requirements.txt   # Project dependencies
  .env.example       # Example environment configuration
  README.md          # User guide & documentation
```

---

## Setup Instructions

### 1. Prerequisites
- **Python 3.8+** installed on your system.
- A **Binance Futures Testnet** account. If you don't have one:
  1. Go to [Binance Futures Testnet](https://testnet.binancefuture.com) and log in (e.g., using your Discord, Google account, or Binance account).
  2. Create/obtain your testnet API keys (API Key & Secret Key).
  3. Ensure your testnet account has some simulated USDT balance (usually credited automatically, but can be refilled via the testnet faucet on the page if needed).

### 2. Environment Setup

Clone this repository or extract the files. Open a terminal in the `trading_bot` directory and run:

#### On Windows (PowerShell/CMD):
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### On macOS/Linux:
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. API Credentials Configuration
Copy the `.env.example` file to `.env`:

```bash
# On Windows
copy .env.example .env

# On macOS/Linux
cp .env.example .env
```

Open `.env` in a text editor and enter your Binance Futures Testnet API credentials:
```env
BINANCE_API_KEY=your_actual_testnet_api_key_here
BINANCE_API_SECRET=your_actual_testnet_api_secret_here
```

---

## How to Run & Examples

Activate the virtual environment if it is not already active, then use `cli.py` to place orders.

### 1. Place a MARKET Order
Market orders do not require a `--price` argument and execute immediately at the current market price.

#### Market BUY Order (e.g., buying 0.01 BTC):
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
```

#### Market SELL Order (e.g., selling 0.05 ETH):
```bash
python cli.py --symbol ETHUSDT --side SELL --type MARKET --quantity 0.05
```

### 2. Place a LIMIT Order
Limit orders require the `--price` argument. They are placed on the order book and will only execute when/if the price reaches the specified limit.

#### Limit BUY Order (e.g., buying 0.01 BTC at $90,000):
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01 --price 90000
```

#### Limit SELL Order (e.g., selling 0.05 ETH at $3,500):
```bash
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.05 --price 3500
```

### 3. Verification of Input Validation
The bot validates all CLI arguments before making any network requests.

#### Missing Price for LIMIT Order:
```bash
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.01
# Result: Displays a validation error card explaining that "Price is required for LIMIT orders."
```

#### Specifying Price for MARKET Order:
```bash
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 --price 95000
# Result: Displays a validation error explaining that "Price cannot be specified for MARKET orders."
```

#### Invalid Symbol:
```bash
python cli.py --symbol INVALID_SYM --side BUY --type MARKET --quantity 1.0
# Result: Displays an error detailing the symbol requirements (alphanumeric, 3-15 chars).
```

---

## Logging System

- All actions, including initializations, network pings, full JSON requests, and raw API responses or errors, are logged to **`trading_bot.log`** located in the root of the execution directory.
- The logger automatically suppresses verbose standard libraries (like `urllib3` or `requests`) to keep the log file readable, focused, and clean.
- The file uses a `RotatingFileHandler` with a maximum size limit (10MB) and keeps up to 5 backups, ensuring that the bot never consumes excessive disk space in long-run environments.

---

## Assumptions & Design Choices

1. **Binance Futures Testnet Override**: We explicitly initialize `python-binance` with `testnet=True` inside `bot/client.py`. This ensures all futures requests automatically hit `https://testnet.binancefuture.com` instead of the live production environment.
2. **Time In Force**: LIMIT orders default to `GTC` (Good 'Til Cancelled). This is standard for futures limit trading.
3. **Precision and Minimums**: Different futures pairs on Binance have specific step-sizes, decimal precision, and minimum order values (e.g., BTCUSDT minimum is typically 0.001 BTC). If you supply a quantity too small or with too many decimals, the Binance API will reject the request. The bot gracefully catches and displays these Binance API exceptions.
4. **Enhanced CLI UX (Bonus)**: Built using the `rich` library, providing a beautiful visual layout, color-coded success/failure cards, animated spinner states, and automated indentation formatting for JSON API logs on-screen.
5. **Lightweight Web UI (Bonus)**: Built using **Streamlit**, providing a fully interactive, responsive web dashboard to monitor balance status, configure keys, execute orders, toggle JSON API payloads, and view real-time log activity on-screen.

---

## Running the Web UI (Bonus)

To launch the interactive web dashboard:

1. Install the updated requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Launch the Streamlit dashboard:
   ```bash
   streamlit run ui.py
   ```
3. The dashboard will automatically open in your default browser at `http://localhost:8501`. 
4. In the sidebar, you can configure your Testnet API Key and Secret (it will load your `.env` values by default if present).
5. Fill out the order form and click **Execute Order** to trade directly on the testnet!

