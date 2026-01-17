import json

class FlashBrief:
  def __init__(self, core):
    self.core = core

  def run(self):
    # 1. Récupération des données nécessaires depuis ta DB
    # On récupère les assets pour calculer la perf globale et les top/flop
    assets = self.core.db.execute("SELECT * FROM user_assets WHERE type = 'CRYPTO'")

    if not assets:
      return "Données insuffisantes pour l'analyse."

    # Calculs rapides pour le prompt
    total_val = sum(a['balance'] * (a['current_price'] or 0) for a in assets)
    # On simule ici les variations 24h (à adapter selon tes colonnes DB)
    # Handle None values in change_24h before sorting
    sorted_assets = sorted(assets, key=lambda x: x.get('change_24h') or 0)

    top_performer = sorted_assets[-1]
    worst_performer = sorted_assets[0]

    # Simulation de la perf BTC (à dynamiser via ton client Binance si besoin)
    btc_asset = next((a for a in assets if a.get('symbol', '').upper() == 'BTC'), None)
    btc_change = btc_asset.get('change_24h') or 0 if btc_asset else 0


    # 3. Appel à Groq
    data = {
      "total_val": round(total_val, 2),
      "top_performer": top_performer,
      "worst_performer": worst_performer,
      "btc_change": btc_change
    }

    flash_brief_analysis = json.loads(self.core.ai.generate_flash_brief(data))
    # Sauvegarde en DB
    self.core.db.execute("""
      INSERT INTO flash_briefs
      (brief, recommendation, global_mood)
      VALUES (%s, %s, %s)
    """, (
      flash_brief_analysis['brief'],
      flash_brief_analysis['recommendation'],
      flash_brief_analysis['global_mood']
    ))


    return True