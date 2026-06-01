#!/usr/bin/env python3
import os
import sys
import argparse
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.json import JSON

# Add the current directory to sys.path so we can import our bot module properly
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot.logging_config import setup_logging
from bot.validators import validate_all, ValidationError
from bot.client import BinanceTestnetClient
from bot.orders import place_futures_order

# Initialize Rich Console
console = Console()

def print_header():
    """Prints a beautiful dashboard header for the trading bot."""
    header_text = Text()
    header_text.append("=== BINANCE FUTURES TRADING BOT ===\n", style="bold gold1")
    header_text.append("Environment: USDT-M Futures Testnet", style="italic steel_blue1")
    console.print(
        Panel(
            header_text,
            border_style="deep_sky_blue1",
            title="[bold sky_blue2]Primetrade.ai Bot[/bold sky_blue2]",
            title_align="center",
            subtitle="[ Status: Active ]",
            subtitle_align="right"
        )
    )

def print_order_request_summary(params: dict):
    """Prints a structured summary of the order being requested."""
    table = Table(title="[bold yellow]Order Request Summary[/bold yellow]", show_header=True, header_style="bold magenta")
    table.add_column("Parameter", style="cyan", width=15)
    table.add_column("Value", style="green")

    table.add_row("Symbol", params["symbol"])
    table.add_row("Side", params["side"])
    table.add_row("Order Type", params["type"])
    table.add_row("Quantity", str(params["quantity"]))
    table.add_row("Price", str(params["price"]) if params["price"] else "MARKET PRICE")
    
    console.print(table)
    console.print("\n")

def main():
    # Load environment variables
    # This searches for .env in the current directory
    load_dotenv()
    
    # Initialize logger
    logger = setup_logging()

    # Parse arguments
    parser = argparse.ArgumentParser(
        description="Place Market or Limit orders on the Binance Futures Testnet (USDT-M)."
    )
    parser.add_argument("--symbol", required=True, help="Trading symbol (e.g., BTCUSDT, ETHUSDT)")
    parser.add_argument("--side", required=True, choices=["BUY", "SELL", "buy", "sell"], help="Order side: BUY or SELL")
    parser.add_argument("--type", required=True, choices=["MARKET", "LIMIT", "market", "limit"], help="Order type: MARKET or LIMIT")
    parser.add_argument("--quantity", required=True, help="Order quantity (positive float/int)")
    parser.add_argument("--price", required=False, default=None, help="Limit price (required only for LIMIT orders)")
    
    args = parser.parse_args()

    print_header()

    # Retrieve API Credentials
    api_key = os.getenv("BINANCE_API_KEY")
    api_secret = os.getenv("BINANCE_API_SECRET")

    if not api_key or not api_secret:
        console.print(
            Panel(
                "[bold red]CRITICAL ERROR: API Credentials Missing[/bold red]\n\n"
                "Please make sure you have created a [yellow].env[/yellow] file in the same directory "
                "with the following keys:\n"
                "[cyan]BINANCE_API_KEY[/cyan]=your_key\n"
                "[cyan]BINANCE_API_SECRET[/cyan]=your_secret\n\n"
                "You can copy [cyan].env.example[/cyan] and fill in your Binance Futures Testnet keys.",
                border_style="red",
                title="Configuration Error"
            )
        )
        logger.error("Execution halted. Binance API credentials were not found in environment variables.")
        sys.exit(1)

    # Validate inputs
    try:
        validated_params = validate_all(
            symbol=args.symbol,
            side=args.side,
            order_type=args.type,
            quantity=args.quantity,
            price=args.price
        )
    except ValidationError as ve:
        console.print(
            Panel(
                f"[bold red]Validation Error:[/bold red] {str(ve)}",
                border_style="red",
                title="Input Validation Failure"
            )
        )
        logger.error("Input validation failed: %s", str(ve))
        sys.exit(1)
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Unexpected Validation Error:[/bold red] {str(e)}",
                border_style="red",
                title="System Error"
            )
        )
        logger.exception("Unexpected error during input validation: %s", str(e))
        sys.exit(1)

    # Print Order Summary
    print_order_request_summary(validated_params)

    # Initialize Binance client and execute order
    try:
        # Initialize client
        client = BinanceTestnetClient(api_key, api_secret)
        
        # Connection check (ping)
        with console.status("[bold blue]Connecting to Binance Futures Testnet...", spinner="dots"):
            client.ping()
            
        # Get Account Balance (helpful context)
        try:
            balance = client.get_account_balance()
            console.print(f"[bold green]Connected successfully![/bold green] Wallet Balance: [bold yellow]{balance} USDT[/bold yellow]\n")
        except Exception:
            console.print("[bold yellow]Warning:[/bold yellow] Connected, but could not retrieve account balance.\n")

        # Placing order
        with console.status("[bold blue]Placing order...", spinner="dots"):
            result = place_futures_order(
                client=client,
                symbol=validated_params["symbol"],
                side=validated_params["side"],
                order_type=validated_params["type"],
                quantity=validated_params["quantity"],
                price=validated_params["price"]
            )

        if result["success"]:
            # Display Success Card
            success_text = Text()
            success_text.append("=== ORDER PLACED SUCCESSFULLY ===\n\n", style="bold green")
            
            table = Table(show_header=False, border_style="dim")
            table.add_column("Key", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Order ID", str(result["order_id"]))
            table.add_row("Status", str(result["status"]))
            table.add_row("Executed Qty", str(result["executed_qty"]))
            table.add_row("Average Price", str(result["avg_price"]))
            
            console.print(
                Panel(
                    table,
                    border_style="green",
                    title="[bold green]Execution Receipt[/bold green]",
                    title_align="center"
                )
            )
            
            # Print minimal raw JSON snippet
            console.print("\n[dim]Raw API Response (Summary):[/dim]")
            console.print_json(data=result["raw_response"])
            
            logger.info("Order executed and CLI printed success receipt.")
            sys.exit(0)
        else:
            # Display Failure Card
            error_msg = result.get("message", "Unknown error")
            code_msg = f" (Code: {result['code']})" if "code" in result else ""
            error_type = result.get("error_type", "APIError")
            
            failure_text = Text()
            failure_text.append(f"=== ORDER PLACEMENT FAILED ===\n\n", style="bold red")
            failure_text.append(f"[bold]Type:[/bold] {error_type}\n", style="red")
            failure_text.append(f"[bold]Details:[/bold] {error_msg}{code_msg}\n\n", style="red")
            failure_text.append("Please verify your API keys, balance, and leverage/margin requirements on the testnet dashboard.", style="italic dim")

            console.print(
                Panel(
                    failure_text,
                    border_style="red",
                    title="[bold red]Execution Failure[/bold red]",
                    title_align="center"
                )
            )
            logger.error("Order placement failed. CLI printed failure message: %s", error_msg)
            sys.exit(1)
            
    except Exception as e:
        console.print(
            Panel(
                f"[bold red]Execution Exception:[/bold red] {str(e)}",
                border_style="red",
                title="System Error"
            )
        )
        logger.exception("An unhandled exception occurred in the CLI layer: %s", str(e))
        sys.exit(1)

if __name__ == "__main__":
    main()
