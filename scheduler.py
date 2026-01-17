import schedule
import time
import subprocess

from datetime import datetime
from main import main as core_entry
from collections import namedtuple

Args = namedtuple('Args', ['command'])

def run(script):
  now = datetime.now().strftime("%H:%M:%S")
  print(f"[{now}] 🚀 Run: {script}\n")
  print("----------- SCRIPT LOGS START -------------")
  # subprocess.run(["./run.sh", script])
  core_entry(Args(command=script))
  print("----------- SCRIPT LOGS END -------------\n")
  print_resume(now, script)

def print_resume(start_time, script):
  end_time = datetime.now().strftime("%H:%M:%S")
  print(f"[{end_time}] ✅ Finished: {script} (started at {start_time})")
  print(f"\n----------------------------------------")
  print("""
📊 Crons summary:

💰 WALLETS & ASSETS:
- Asset Prices Sync: every 10 minutes
- Wallet Sync: every 1 hour

📰 NEWS INGESTION:
- Finnhub: every 15 minutes
- GNews: every 1 hour
- CryptoPanic: every 8 hours

🧠 INTELLIGENCE
- Daily Market & Wallet Intelligence & Stocks: every day at 06:00 AM
- Daily Flash Brief: every 1 hour
""")
  print(f"----------------------------------------\n")

# Planification

schedule.every(30).minutes.do(run, "news:gnews")
schedule.every(8).hours.do(run, "news:cryptopanic")
schedule.every(15).minutes.do(run, "news:finnhub")

schedule.every(10).minutes.do(run, "assets:prices_sync")

schedule.every().hour.do(run, "wallet:sync")

schedule.every().hour.do(run, "intelligence:flash_brief")

schedule.every().day.at("06:00").do(run, "intelligence:market")
schedule.every().day.at("06:00").do(run, "intelligence:wallet")
schedule.every().day.at("06:00").do(run, "intelligence:stocks")

schedule.every().day.at("23:50").do(run, "wallet:snapshot")



print("🟢 Omega Intelligence Suite started\n")

run("assets:prices_sync")

while True:
    schedule.run_pending()
    time.sleep(1)