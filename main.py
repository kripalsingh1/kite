
import logging
import time
import datetime as dt
from kiteconnect import KiteConnect
import threading
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - %(message)s')

API_KEY = os.getenv("API_KEY")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

kite = KiteConnect(api_key=API_KEY)
kite.set_access_token(ACCESS_TOKEN)

ENTRY_TIME = dt.time(10, 0)
STRIKE_ENTRY_PRICE = 366
STOP_LOSS = 315
TRAIL_SL = 365
TARGET_1 = 460
TARGET_2 = 465

def fetch_instruments():
    instruments = kite.instruments("NSE")
    banknifty_options = []
    today = dt.datetime.now().date()

    for ins in instruments:
        if "BANKNIFTY" in ins["tradingsymbol"] and ins["segment"] == "NFO-OPT" and ins["expiry"] >= today:
            banknifty_options.append(ins)

    return banknifty_options

def fetch_ltp(symbol):
    try:
        return kite.ltp(f"NFO:{symbol}")[f"NFO:{symbol}"]["last_price"]
    except Exception as e:
        logging.error(f"LTP fetch error for {symbol}: {e}")
        return None

def monitor_trade(symbol):
    entry_done = False
    sl = STOP_LOSS
    while True:
        ltp = fetch_ltp(symbol)
        if not ltp:
            time.sleep(5)
            continue

        if not entry_done and ltp >= STRIKE_ENTRY_PRICE:
            logging.info(f"Signal: Entry in {symbol} at {ltp}")
            entry_done = True

        elif entry_done:
            if ltp <= sl:
                logging.info(f"SL hit for {symbol} at {ltp}")
                break
            elif ltp >= TARGET_2:
                logging.info(f"Final target hit for {symbol} at {ltp}. Exiting...")
                break
            elif ltp >= TARGET_1:
                sl = TRAIL_SL
                logging.info(f"Trail SL activated for {symbol}")

        time.sleep(5)

def monitor_options():
    instruments = fetch_instruments()
    checked = set()

    while True:
        now = dt.datetime.now().time()
        if now < ENTRY_TIME:
            logging.info("Waiting for 10:00 AM...")
            time.sleep(30)
            continue

        for ins in instruments:
            symbol = ins["tradingsymbol"]
            if symbol in checked:
                continue

            ltp = fetch_ltp(symbol)
            if not ltp:
                continue

            if ltp >= STRIKE_ENTRY_PRICE:
                try:
                    quote = kite.quote(f"NFO:{symbol}")
                    day_high = quote[f"NFO:{symbol}"]["ohlc"]["high"]

                    if day_high < STRIKE_ENTRY_PRICE:
                        logging.info(f"{symbol} day high {day_high} broken with LTP {ltp}")
                        threading.Thread(target=monitor_trade, args=(symbol,), daemon=True).start()
                        checked.add(symbol)
                except Exception as e:
                    logging.error(f"Error fetching day high for {symbol}: {e}")

        time.sleep(5)

if __name__ == "__main__":
    logging.info("Starting BankNifty Paper Trading Bot...")
    monitor_options()
