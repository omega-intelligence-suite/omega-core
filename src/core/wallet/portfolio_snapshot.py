import requests

class PortfolioSnapshot:
  def __init__(self, core):
     self.core = core

  def get_exchange_rate(self):
    """Récupère le taux de change USD/EUR (1 USD = X EUR)"""
    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=10)
        data = response.json()
        return data['rates']['EUR']
    except Exception as e:
        print(f"⚠️ Erreur taux de change, repli sur 0.92 : {e}")
        return 0.92

  def run(self):
    try:
      usd_to_eur = self.get_exchange_rate()

      # 1. Récupérer les actifs actuels
      my_assets = self.core.db.execute("SELECT * FROM user_assets")

      if not my_assets: return

      total_value_eur = 0
      total_invested_eur = 0
      btc_price_usd = 0 # Changement ici : on vise l'USD

      # 2. Analyse et Conversion
      for asset in my_assets:
        price_orig = asset.get('current_price', 0) or 0
        pru_orig = asset.get('average_price', 0) or 0
        qty = asset.get('balance', 0) or 0
        a_type = asset.get('type', '').lower()

        print(f"price_orig: {price_orig} | pru_orig: {pru_orig} | qty: {qty} | type: {a_type}")
        # Logique de conversion pour le total patrimoine (EUR)
        if a_type == 'crypto':
          price_eur = price_orig * usd_to_eur
          pru_eur = pru_orig * usd_to_eur
          # Capture spécifique du prix BTC en USD
          if asset['symbol'].upper() == 'BTC':
            btc_price_usd = price_orig
        else:
          price_eur = price_orig
          pru_eur = pru_orig

        total_value_eur += (qty * (price_eur or 0))
        total_invested_eur += (qty * (pru_eur or 0))
        # print(f"{price_eur} | {pru_eur} | {qty} | {a_type} => +{qty * price_eur} EUR")

      # 3. Insertion Snapshot Global
      snapshot_data = {
        "total_value_eur": total_value_eur,
        "total_invested_eur": total_invested_eur,
        "btc_price_usd": btc_price_usd, # Stocké en USD
        "daily_pnl_eur": total_value_eur - total_invested_eur,
        "usd_eur_rate": usd_to_eur
      }

      print("Snapshot Data:", snapshot_data)

      snap_result = self.core.db.execute(
        """INSERT INTO portfolio_snapshots
            (total_value_eur, total_invested_eur, btc_price_usd, daily_pnl_eur, usd_eur_rate)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id""",
        (total_value_eur, total_invested_eur, btc_price_usd, total_value_eur - total_invested_eur, usd_to_eur)
      )

      snapshot_id = snap_result[0]['id']

      # 4. Insertion Détails (Bulk)
      assets_history = []
      for asset in my_assets:
        qty = asset.get('balance', 0) or 0
        p_orig = asset.get('current_price', 0) or 0
        a_type = asset.get('type', '').lower()

        # Calcul des valeurs en EUR et USD selon le type
        if a_type == 'crypto':
          v_usd = qty * p_orig  # Cryptos en USD
          v_eur = v_usd * usd_to_eur
        else:
          v_eur = qty * p_orig  # Stocks/Bank en EUR
          v_usd = v_eur / usd_to_eur

        assets_history.append({
          "snapshot_id": snapshot_id,
          "symbol": asset['symbol'],
          "balance": qty,
          "price_at_snapshot": p_orig, # Prix dans la devise d'origine (USD pour crypto, EUR pour le reste)
          "value_eur": v_eur,
          "value_usd": v_usd,
          "asset_type": asset.get('type', '')
        })

        self.core.db.execute("""
          INSERT INTO portfolio_assets_history
          (snapshot_id, symbol, name, balance, price_at_snapshot, value_eur, value_usd, asset_type)
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
          snapshot_id,
          asset['symbol'],
          asset.get('name', ''),
          qty,
          p_orig,
          v_eur,
          v_usd,
          asset.get('type', '')
        ))

      print(f"✅ Snapshot réussi. Valeur: {total_value_eur:.2f}€ | BTC: ${btc_price_usd:,.0f}")
      return True

    except Exception as e:
        print(f"🔥 Erreur Critique : {e}")

if __name__ == "__main__":
    take_daily_snapshot()