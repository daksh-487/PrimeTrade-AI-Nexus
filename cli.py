import sys
import click
from tabulate import tabulate
import colorama
from colorama import Fore, Style
colorama.init(autoreset=True)

from bot.client import BinanceClient
from bot.orders import OrderManager
from bot.ai_advisor import AIAdvisor
from bot import validators
from bot.logging_config import get_logger

logger = get_logger(__name__)

from functools import wraps

def handle_error(func):
    """Global click error handler for unhandled exceptions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            click.echo(Fore.RED + Style.BRIGHT + f"\n[!] Error: {str(e)}")
            logger.error(f"CLI Error: {str(e)}", exc_info=True)
            sys.exit(1)
    return wrapper

@click.group()
def cli():
    """PrimeTrade Bot - CLI for placing Binance Futures orders (Testnet)."""
    pass

@cli.command()
@handle_error
@click.option('--symbol', required=True, type=str, help='Trading pair e.g. BTCUSDT')
@click.option('--side', required=True, type=str, help='BUY or SELL')
@click.option('--type', 'order_type', required=True, type=str, help='MARKET, LIMIT, or STOP_LIMIT')
@click.option('--quantity', required=True, type=float, help='Order quantity')
@click.option('--price', type=float, help='Limit price (required for LIMIT/STOP_LIMIT)')
@click.option('--stop-price', type=float, help='Stop price (required for STOP_LIMIT)')
def place_order(symbol, side, order_type, quantity, price, stop_price):
    """Places a new order on Binance Futures Testnet."""
    
    # 1. Validation
    sym = validators.validate_symbol(symbol)
    sd = validators.validate_side(side)
    typ = validators.validate_order_type(order_type)
    qty = validators.validate_quantity(str(quantity))
    pr = validators.validate_price(str(price) if price else None, typ)
    sp = validators.validate_stop_price(str(stop_price) if stop_price else None, typ)

    # 2. Setup Client & Advisor
    client = BinanceClient()
    manager = OrderManager(client)
    advisor = AIAdvisor()

    # 3. Print Summary BEFORE order
    click.echo(Fore.CYAN + Style.BRIGHT + "\n=== Order Summary ===")
    click.echo(Fore.WHITE + f"Symbol     : {sym}")
    qty_col = Fore.GREEN if sd == "BUY" else Fore.RED
    click.echo(qty_col + f"Side       : {sd}")
    click.echo(Fore.WHITE + f"Type       : {typ}")
    click.echo(Fore.WHITE + f"Quantity   : {qty}")
    if pr:
        click.echo(Fore.WHITE + f"Price      : {pr}")
    if sp:
        click.echo(Fore.WHITE + f"Stop Price : {sp}")
        
    # AI Risk Advisory
    click.echo("\n" + Fore.YELLOW + "🤖 AI Risk Advisory" + Style.RESET_ALL)
    click.echo(Fore.YELLOW + "-------------------")
    ai_risk = advisor.analyze_order(sym, sd, typ, qty, pr)
    click.echo(Fore.YELLOW + ai_risk + Style.RESET_ALL)
    click.echo("")

    # 4. Confirmation
    if not click.confirm('Confirm order?'):
        click.echo(Fore.YELLOW + "Order cancelled.")
        return

    # 5. Place Order
    click.echo(Fore.CYAN + "Placing order... Please wait.")
    
    result = {}
    if typ == "MARKET":
        result = manager.place_market_order(sym, sd, qty)
    elif typ == "LIMIT":
        result = manager.place_limit_order(sym, sd, qty, pr)
    elif typ == "STOP_LIMIT":
        result = manager.place_stop_limit_order(sym, sd, qty, pr, sp)

    # 6. Success Output
    click.echo(Fore.GREEN + Style.BRIGHT + "\n✅ Order Placed Successfully!\n")
    
    # Format table using tabulate
    table_data = [[k, v] for k, v in result.items()]
    click.echo(tabulate(table_data, headers=["Field", "Value"], tablefmt="fancy_grid"))
    
    logger.info(f"Order successfully placed. Result: {result}")

    # AI Post-Order Explanation
    click.echo("\n" + Fore.CYAN + "🤖 AI Order Summary" + Style.RESET_ALL)
    click.echo(Fore.CYAN + "-------------------")
    ai_summary = advisor.explain_order_result(result)
    click.echo(Fore.CYAN + ai_summary + Style.RESET_ALL)
    click.echo("")

@cli.command()
@handle_error
def check_connection():
    """Tests API connection and prints account balance summary."""
    client = BinanceClient()
    result = client.test_connection()
    click.echo(Fore.GREEN + "\nConnection Successful!")
    click.echo(Fore.WHITE + f"Can Trade    : {result.get('canTrade')}")
    click.echo(Fore.WHITE + f"USDT Balance : {result.get('usdt_balance')}")

@cli.command()
@handle_error
@click.option('--symbol', required=True, type=str, help='Trading pair e.g. BTCUSDT')
@click.option('--order-id', required=True, type=int, help='Numeric Order ID to fetch')
def order_status(symbol, order_id):
    """Fetches and displays order status."""
    sym = validators.validate_symbol(symbol)
    
    client = BinanceClient()
    manager = OrderManager(client)
    
    click.echo(Fore.CYAN + f"Fetching status for Order {order_id} ({sym})...")
    result = manager.get_order_status(sym, order_id)
    
    status_col = Fore.GREEN if result.get('status') == 'FILLED' else Fore.YELLOW
    if result.get('status') in ['CANCELED', 'EXPIRED', 'REJECTED']:
        status_col = Fore.RED

    click.echo(status_col + f"\nStatus: {result.get('status')}")
    table_data = [[k, v] for k, v in result.items()]
    click.echo(tabulate(table_data, headers=["Field", "Value"], tablefmt="fancy_grid"))

if __name__ == '__main__':
    cli()
