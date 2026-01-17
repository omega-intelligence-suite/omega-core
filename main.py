import argparse
from dotenv import load_dotenv

from src.api.database import Database
from src.domain import AI, Telegram
from src.core.news import CryptoPanicNewsIngestion, GNewsNewsIngestion, FinnhubNewsIngestion
from src.core.wallet import BinanceSynchro, PortfolioSnapshot
from src.core.assets import AssetsPriceSynchro
from src.core.intelligence import FlashBrief, MarketIntelligence, StocksIntelligence, WalletIntelligence


load_dotenv()

class Core:
  def __init__(self):
    self.db = Database()
    self.db.connect()
    self.ai = AI()
    self.telegram = Telegram()

COMMAND_TREE = {
  'wallet': {
    'sync': BinanceSynchro,
    'snapshot': PortfolioSnapshot,
  },
  'news': {
    'cryptopanic': CryptoPanicNewsIngestion,
    'gnews': GNewsNewsIngestion,
    'finnhub': FinnhubNewsIngestion,
  },
  'assets': {
    'prices_sync': AssetsPriceSynchro,
  },
  'intelligence': {
    'flash_brief': FlashBrief,
    'market': MarketIntelligence,
    'stocks': StocksIntelligence,
    'wallet': WalletIntelligence,
  },
}

def get_available_commands():
  """Generate list of available commands from the tree"""
  commands = []
  for category, tasks in COMMAND_TREE.items():
    for task_name in tasks.keys():
      commands.append(f"{category}:{task_name}")
  return commands

def run_command(command_str, core):
  """Parse and execute a command from the tree"""
  try:
    category, task = command_str.split(':')

    if category not in COMMAND_TREE:
      print(f"❌ Unknown category: {category}")
      return False

    if task not in COMMAND_TREE[category]:
      print(f"❌ Unknown task '{task}' in category '{category}'")
      return False

    TaskClass = COMMAND_TREE[category][task]
    print(f"🚀 Running {category}:{task}...")
    return TaskClass(core).run()

  except ValueError:
    print(f"❌ Invalid command format. Use 'category:task' (e.g., 'news:gnews')")
    return False

def main(args):
  success = False
  core = Core()

  try:
    success = run_command(args.command, core)

    if success:
      print("✅ Process completed successfully.")
    else:
      print("❌ Process failed.")
  finally:
    core.db.close()



def parse_args():
  """Main entry point with argument parsing"""
  parser = argparse.ArgumentParser(
    description='Omega Intelligence Suite Core',
    epilog=f"Available commands: {', '.join(get_available_commands())}"
  )
  parser.add_argument(
    'command',
    help='Command to run in format category:task (e.g., news:gnews, wallet:sync)'
  )

  args = parser.parse_args()
  main(args)



if __name__ == "__main__":
  parse_args()
