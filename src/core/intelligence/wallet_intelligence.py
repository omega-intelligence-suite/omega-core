from datetime import datetime
import json
import os

class WalletIntelligence:
  def __init__(self, core):
    self.core = core
    self.OWNER_ID = os.getenv("OMEGA_OWNER_ID")

  def run(self):
    fetched_data = self.fetch_portfolio_data()
    analysis = json.loads(self.core.ai.analyze_portfolio(fetched_data))
    print("→ Wallet Intelligence Analysis:")
    print("→ Summary:", analysis)

    self.core.db.execute("""
      INSERT INTO wallet_briefs
      (summary, risk_score, narrative_score, velocity_score, btc_accumulation_index, user_id)
      VALUES (%s, %s, %s, %s, %s, %s)
    """, (
      analysis['summary'],
      analysis['risk_score'],
      analysis['narrative_score'],
      analysis['velocity_score'],
      analysis['btc_accumulation_index'],
      self.OWNER_ID
    ))
    return True



  def fetch_portfolio_data(self):
    # 1. Récupérer les assets et leurs cibles
    assets = self.core.db.execute("""
      SELECT a.*, at.*
      FROM user_assets a
      LEFT JOIN asset_targets at ON a.symbol = at.symbol
      WHERE a.type = 'CRYPTO'
    """)

    total_value = sum(a['balance'] * a['current_price'] for a in assets if a['current_price'])

    # 2. Préparation du contexte pour l'IA
    portfolio_summary = []
    for a in assets:
      val = a['balance'] * (a['current_price'] or 0)
      allocation = (val / total_value) * 100 if total_value > 0 else 0
      target = a['target_price_usd'] if a['target_price_usd'] else None

      portfolio_summary.append({
        "asset": a['symbol'],
        "value_usd": round(val, 2),
        "allocation_pct": round(allocation, 2),
        "pnl_pct": round(((a['current_price'] - a['average_price']) / (a['average_price'] or 1) * 100), 2) if a['average_price'] else 0,
        "dist_to_target_pct": round(((target - a['current_price']) / target * 100), 2) if target else "N/A"
      })

    return {
      "total_value": round(total_value, 2),
      "assets": portfolio_summary,
      "market_context": {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "btc_dominance": "52.4%", # À dynamiser via API plus tard
        "fear_greed_index": 68    # À dynamiser via API plus tard
      }
    }
