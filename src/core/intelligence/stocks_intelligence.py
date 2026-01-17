import json
from datetime import datetime

class StocksIntelligence:
  def __init__(self, core):
    self.core = core

  def run(self):
    print("🔄 Starting Stocks Intelligence analysis...")
    fetched_stocks = self._fetch_stocks_data()
    analysis = json.loads(self.core.ai.analyze_stocks_portfolio(fetched_stocks))
    print("→ Stocks Intelligence Analysis:")
    print("→ Summary:", analysis)

    self.core.db.execute("""
      INSERT INTO stocks_briefs
      (summary)
      VALUES (%s)
    """, (
      analysis['summary'],
    ))

    return True

  def _fetch_stocks_data(self):
  # 1. Récupérer les assets et leurs cibles
    assets = self.core.db.execute("""
      SELECT *
      FROM user_assets
      WHERE type = 'STOCKS_ETFS'
    """)

    total_value = sum(a['balance'] * a['current_price'] for a in assets if a['current_price'])

    # 2. Préparation du contexte pour l'IA
    portfolio_summary = []
    for a in assets:
      current_p = a.get('current_price')
      val_totale = float(a['balance']) * float(current_p)

      portfolio_summary.append({
        "name": a['name'],
        "ticker": a['symbol'],
        "quantity": a['balance'],
        "avg_price": a['average_price'],
        "current_price": current_p,
        "total_value": round(val_totale, 2)
      })

    # Calcul des pourcentages de répartition réels
    for item in portfolio_summary:
      item['repartition_pct'] = round((item['total_value'] / total_value) * 100, 2)

    return {
      "total_value": round(total_value, 2),
      "assets": portfolio_summary,
      "market_context": {
        "date": datetime.now().strftime("%Y-%m-%d"),
      }
    }