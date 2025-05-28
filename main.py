
from datetime import datetime
import pytz
import time

# Set timezone to IST (Asia/Kolkata)
india = pytz.timezone('Asia/Kolkata')

print("[INFO] Starting BankNifty Paper Trading Bot...")

while True:
    now = datetime.now(india)
    if now.hour < 10:
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Waiting for 10:00 AM...")
        time.sleep(60)
    else:
        print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] ✅ Time crossed 10:00 AM! Starting trade monitoring...")
        break
