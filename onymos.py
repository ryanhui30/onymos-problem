import threading
import random
import time
from collections import deque

# Global lock for thread safety
lock = threading.Lock()

# Order book: Each stock has separate buy and sell order queues
MAX_TICKERS = 1024  # Limit on the number of different stocks being traded
buy_orders = [deque() for _ in range(MAX_TICKERS)]  # Stores buy orders per stock
sell_orders = [deque() for _ in range(MAX_TICKERS)]  # Stores sell orders per stock

# Function to add a new order (Buy/Sell)
def addOrder(order_type, ticker, quantity, price):
    """
    Adds a new order to the order book.
    :param order_type: 'Buy' or 'Sell'
    :param ticker: Stock ticker index (0 - 1023)
    :param quantity: Number of shares
    :param price: Price per share
    """
    order = (price, quantity)  # Store as tuple to maintain order book structure
    with lock:  # Ensure thread safety when modifying shared data
        if order_type == 'Buy':
            buy_orders[ticker].append(order)  # Add to the buy order queue
        else:
            sell_orders[ticker].append(order)  # Add to the sell order queue

# Function to match buy and sell orders
def matchOrder():
    """
    Matches buy and sell orders for all tickers in the system.
    - Matches the highest Buy price with the lowest Sell price.
    - Ensures thread safety and O(n) complexity.
    """
    with lock:
        for ticker in range(MAX_TICKERS):
            while buy_orders[ticker] and sell_orders[ticker]:
                buy_price, buy_quantity = buy_orders[ticker][0]  # Get highest priority buy order
                sell_price, sell_quantity = sell_orders[ticker][0]  # Get lowest priority sell order

                if buy_price >= sell_price:  # Match condition
                    match_quantity = min(buy_quantity, sell_quantity)  # Execute trade for min quantity

                    # Print matched trade details
                    print(f"Matched: Ticker {ticker} | Price {sell_price:.2f} | Quantity {match_quantity}")

                    # Update remaining quantities
                    if buy_quantity > match_quantity:
                        buy_orders[ticker][0] = (buy_price, buy_quantity - match_quantity)
                    else:
                        buy_orders[ticker].popleft()

                    if sell_quantity > match_quantity:
                        sell_orders[ticker][0] = (sell_price, sell_quantity - match_quantity)
                    else:
                        sell_orders[ticker].popleft()
                else:
                    break  # No more matches possible

# Function to simulate random stock transactions
def simulateOrders():
    """
    Generates random Buy and Sell orders for different tickers to simulate a live trading engine.
    """
    while True:
        order_type = random.choice(['Buy', 'Sell'])
        ticker = random.randint(0, MAX_TICKERS - 1)  # Random ticker
        quantity = random.randint(1, 100)  # Random quantity (1-100 shares)
        price = round(random.uniform(10, 400), 2)  # Random price (between $10 and $400)

        addOrder(order_type, ticker, quantity, price)  # Add order to the book
        matchOrder()  # Try to match orders

        time.sleep(random.uniform(0.01, 0.1))  # Random delay to simulate real-time trades

# Start simulation in a separate thread to mimic real-time trading
threading.Thread(target=simulateOrders, daemon=True).start()

# Keep the program running
try:
    while True:
        time.sleep(1)  # Let the simulation run
except KeyboardInterrupt: # Stop the simulation when user presses Ctrl+C
    print("Trading simulation stopped.")
