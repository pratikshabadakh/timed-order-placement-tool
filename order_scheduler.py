# order_scheduler.py

from SmartApi.smartConnect import SmartConnect
from dotenv import load_dotenv
import os
import datetime
import time
import schedule
import csv

# -------------------------------
# Step 1: Load API Credentials
# -------------------------------
load_dotenv()
api_key = os.getenv("API_KEY")
client_code = os.getenv("CLIENT_CODE")
password = os.getenv("CLIENT_PASSWORD")
totp = os.getenv("TOTP")

# -------------------------------
# Step 2: Login to Angel One API
# -------------------------------
try:
    obj = SmartConnect(api_key=api_key)
    data = obj.generateSession(client_code, password, totp)
    refresh_token = data['data']['refreshToken']
    print("Login Successful!")
except Exception as e:
    print("Login Failed:", e)
    exit()

# -------------------------------
# Step 3: Order Logger to CSV
# -------------------------------
def log_order(symbol, qty, otype, status, order_id):
    with open("order_log.csv", "a", newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            symbol, qty, otype, status, order_id
        ])

# -------------------------------
# Step 4: Take User Inputs
# -------------------------------
symbol = input("Enter Trading Symbol (e.g., SBIN-EQ): ").strip()
token = input("Enter Symbol Token: ").strip()
side = input("BUY or SELL?: ").upper()
otype = input("MARKET or LIMIT?: ").upper()
qty = input("Quantity to buy/sell: ").strip()
ptype = input("Product Type (INTRADAY or DELIVERY): ").upper()
repeat_count = int(input("Number of times to repeat order: ").strip())
order_time = input("Enter time to place order (HH:MM 24h format): ").strip()

# -------------------------------
# Step 5: Order Placement
# -------------------------------
def place_order():
    try:
        order_params = {
            "variety": "NORMAL",
            "tradingsymbol": symbol,
            "symboltoken": token,
            "transactiontype": side,
            "exchange": "NSE",
            "ordertype": otype,
            "producttype": ptype,
            "duration": "DAY",
            "price": "0",   # Use "0" for MARKET order
            "squareoff": "0",
            "stoploss": "0",
            "quantity": qty
        }

        response = obj.placeOrder(order_params)
        print("Full API Response:", response)

        # Fix: If response is just a string (order ID), log it
        if isinstance(response, str):
            order_id = response
        elif isinstance(response, dict) and "data" in response and "orderid" in response["data"]:
            order_id = response["data"]["orderid"]
        else:
            order_id = "N/A"

        if order_id != "N/A":
            print("Order Placed! ID:", order_id)
            log_order(symbol, qty, side, "Success", order_id)
        else:
            print("Order Rejected. No Order ID.")
            log_order(symbol, qty, side, "Failed", "N/A")

    except Exception as e:
        print("Order Failed:", e)
        log_order(symbol, qty, side, "Failed", "N/A")

# -------------------------------
# Step 6: Schedule the Orders
# -------------------------------
def schedule_order():
    count = {"executions": 0}

    def limited_order():
        if count["executions"] < repeat_count:
            place_order()
            count["executions"] += 1
        else:
            print("All repeated orders completed.")
            return schedule.CancelJob

    schedule.every().day.at(order_time).do(limited_order)
    print(f"🕒 Order scheduled for {order_time} (will repeat {repeat_count} times)")

    while True:
        schedule.run_pending()
        time.sleep(1)

# Run the script
schedule_order()