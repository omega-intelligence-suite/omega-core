import os
from binance.client import Client

class BinanceSynchro:
  def __init__(self, core):
    self.client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'))
    self.core = core
    self.OWNER_ID = os.getenv("OMEGA_OWNER_ID")

  def run(self):
    print("Running Binance synchronization...")

    info = self.client.get_account()
    balances = info['balances']

    # Dictionnaire temporaire pour cumuler les soldes
    wallet_summary = {}

    for asset in balances:
      raw_symbol = asset['asset']
      total_val = float(asset['free']) + float(asset['locked'])

      if total_val > 0:
        clean_symbol = self.clean_asset_name(raw_symbol)

        if clean_symbol in wallet_summary:
          wallet_summary[clean_symbol] += total_val
        else:
          wallet_summary[clean_symbol] = total_val

    print("Wallet Summary:", wallet_summary)

    # Sync wallet to database
    for symbol, balance in wallet_summary.items():
      self.sync_asset_to_db(symbol, balance)

    print(f"✅ Synced {len(wallet_summary)} assets to database.")
    return True

  def sync_asset_to_db(self, symbol, balance):
    """Check if asset exists, update or create accordingly"""

    # Check if asset already exists
    existing_asset = self.core.db.execute(
      "SELECT id, balance FROM user_assets WHERE symbol = %s AND type = 'CRYPTO'",
      (symbol,)
    )

    if existing_asset and len(existing_asset) > 0:
      # Asset exists - update if balance changed
      asset_id = existing_asset[0]['id']
      current_balance = float(existing_asset[0]['balance'])

      self.core.db.execute(
        """UPDATE user_assets
            SET balance = %s, last_wallet_sync_at = NOW()
            WHERE id = %s""",
        (balance, asset_id)
      )
      print(f"  Updated {symbol}: {current_balance} → {balance}")
    else:
      # Asset doesn't exist - create new entry
      self.core.db.execute(
        """INSERT INTO user_assets (symbol, balance, type, user_id)
           VALUES (%s, %s, 'CRYPTO', %s)""",
        (symbol, balance, self.OWNER_ID)
      )
      self.core.db.commit()
      print(f"  Created {symbol}: {balance}")

    return True

  def clean_asset_name(self, asset_name):
    # Enlève le préfixe 'LD' si présent (Binance Earn)
    if asset_name.startswith('LD') and len(asset_name) > 2:
        # Cas particulier : ne pas transformer 'LDO' (Lido DAO) en 'O'
        if asset_name == 'LDO':
            return 'LDO'
        return asset_name[2:]
    return asset_name