import os
import sys
import streamlit as st
from dotenv import load_dotenv

# Add current directory to path to enable package imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging
from bot.validators import validate_all, ValidationError
from bot.client import BinanceTestnetClient
from bot.orders import place_futures_order

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Primetrade.ai Trading Bot Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize logger
logger = setup_logging()

# Custom Styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #FFB300;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #78909C;
        margin-bottom: 2rem;
    }
    .card {
        padding: 1.5rem;
        border-radius: 8px;
        background-color: #1E293B;
        border: 1px solid #334155;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - API Credentials configuration
st.sidebar.markdown("### 🔑 API Configuration")
api_key_env = os.getenv("BINANCE_API_KEY", "")
api_secret_env = os.getenv("BINANCE_API_SECRET", "")

api_key = st.sidebar.text_input("Binance API Key", value=api_key_env, type="password")
api_secret = st.sidebar.text_input("Binance API Secret", value=api_secret_env, type="password")

st.sidebar.markdown("---")
st.sidebar.markdown("### ℹ️ Environment Info")
st.sidebar.info("Target Environment: **Binance Futures Testnet (USDT-M)**\n\nBase URL: `https://testnet.binancefuture.com`")

# Main Content Header
st.markdown('<div class="main-header">⚡ Binance Futures Trading Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A lightweight interactive web UI for placing Market and Limit orders on USDT-M Futures Testnet</div>', unsafe_allow_html=True)

# Connectivity & Account Summary Block
if not api_key or not api_secret:
    st.warning("⚠️ Please configure your Binance Futures Testnet API Key and Secret in the sidebar to get started.")
else:
    # Attempt to initialize client and fetch balance
    try:
        client = BinanceTestnetClient(api_key, api_secret)
        
        # Connection check (ping)
        client.ping()
        
        # Get Balance
        balance = client.get_account_balance()
        
        # Display balance metric
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="USDT Wallet Balance", value=f"{balance:.4f} USDT", delta="Active Connection", delta_color="normal")
        with col2:
            st.metric(label="Target Market", value="USDT-M Futures", delta="Testnet", delta_color="off")
            
    except Exception as e:
        st.error(f"❌ Failed to connect to Binance Futures Testnet. Please verify your credentials.\nError: {str(e)}")

# Order Placement form
st.markdown("### 📥 Place a New Order")

order_form = st.container()
with order_form:
    col_sym, col_side, col_type = st.columns(3)
    
    with col_sym:
        symbol = st.text_input("Trading Symbol", value="BTCUSDT", help="e.g. BTCUSDT, ETHUSDT").strip().upper()
        
    with col_side:
        side = st.selectbox("Side", options=["BUY", "SELL"])
        
    with col_type:
        order_type = st.selectbox("Order Type", options=["MARKET", "LIMIT"])
        
    col_qty, col_price = st.columns(2)
    
    with col_qty:
        quantity = st.text_input("Quantity", value="0.005", help="e.g., 0.005 for BTC")
        
    with col_price:
        if order_type == "LIMIT":
            price = st.text_input("Price (USDT)", value="60000.0", help="Limit price is required for LIMIT orders")
        else:
            price = st.text_input("Price (USDT)", value="", disabled=True, placeholder="Market price will be used")

    # Place order action
    submit_btn = st.button("🚀 Execute Order", use_container_width=True)

    if submit_btn:
        if not api_key or not api_secret:
            st.error("Cannot execute order: API Keys are not configured in the sidebar!")
        else:
            # Perform inputs validation
            try:
                validated = validate_all(
                    symbol=symbol,
                    side=side,
                    order_type=order_type,
                    quantity=quantity,
                    price=price if order_type == "LIMIT" else None
                )
                
                st.info("Input validation success! Sending order to Binance Futures Testnet...")
                
                # Execute order
                client = BinanceTestnetClient(api_key, api_secret)
                result = place_futures_order(
                    client=client,
                    symbol=validated["symbol"],
                    side=validated["side"],
                    order_type=validated["type"],
                    quantity=validated["quantity"],
                    price=validated["price"]
                )
                
                if result["success"]:
                    st.success("🎉 Order Executed Successfully!")
                    
                    # Display structured details card
                    col_res1, col_res2, col_res3, col_res4 = st.columns(4)
                    with col_res1:
                        st.metric("Order ID", str(result["order_id"]))
                    with col_res2:
                        st.metric("Status", str(result["status"]))
                    with col_res3:
                        st.metric("Executed Qty", str(result["executed_qty"]))
                    with col_res4:
                        st.metric("Average Price", str(result["avg_price"]))
                        
                    # Raw API Response Toggle
                    with st.expander("📝 View Full API Response Payload"):
                        st.json(result["raw_response"])
                else:
                    error_msg = result.get("message", "Unknown error occurred")
                    st.error(f"❌ Order Execution Failed!\n\n**Type:** {result.get('error_type', 'APIError')}\n\n**Details:** {error_msg}")
                    
            except ValidationError as ve:
                st.error(f"⚠️ Validation Error: {str(ve)}")
            except Exception as e:
                st.error(f"💥 System Error during order execution: {str(e)}")

# Logs View section
st.markdown("---")
st.markdown("### 📋 System Activity Logs")
try:
    log_path = "trading_bot.log"
    if os.path.exists(log_path):
        with open(log_path, "r", encoding="utf-8") as f:
            log_lines = f.readlines()
        
        # Display last 30 log lines
        recent_logs = "".join(log_lines[-30:])
        st.code(recent_logs, language="text")
    else:
        st.info("No system activity logs found yet. Execute an order to generate logs.")
except Exception as e:
    st.warning(f"Could not load log file: {str(e)}")
