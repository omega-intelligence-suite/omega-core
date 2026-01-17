import json
import os
import requests

from datetime import datetime

class MarketIntelligence:
  def __init__(self, core):
    self.core = core
    self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
    self.telegram_token = os.getenv('TELEGRAM_BOT_TOKEN')
    self.OWNER_ID = os.getenv("OMEGA_OWNER_ID")

  def run(self):
    news = self.core.db.execute("""
      SELECT title, summary_short AS description
      FROM news_signals
      ORDER BY published_at DESC
      LIMIT 10
    """)

    if not news:
      print("❌ No news data available for intelligence analysis.")
      return False
    else:
      analysis = json.loads(self.core.ai.analyze_market(news))
      print("→ Market Intelligence Analysis:")
      print(analysis['brief'])

    self.core.db.execute("""
      INSERT INTO market_briefs
      (brief, focus, sentiment, user_id)
      VALUES (%s, %s, %s, %s)
    """, (
      analysis['brief'],
      analysis['focus'],
      analysis['sentiment'],
      self.OWNER_ID
    ))

    self.dispatch_market_analysis(analysis['brief'], analysis['sentiment'], analysis['focus'])
    return True

  def dispatch_market_analysis(self, text, sentiment, focus):
    """Envoie le flash d'analyse directement sur Telegram"""
    emoji_map = {
      "BULLISH": "🟢",
      "BEARISH": "🔴",
      "NEUTRAL": "🟡"
    }
    sentiment_emoji = emoji_map.get(sentiment, "⚫")
    message = f"""
🤖 *OMEGA INTELLIGENCE - BRIEFING 6AM* _({datetime.now().strftime('%Y/%m/%d')})_\n
📊 *Summary*:
{text}\n
💁‍♂️ *Sentiment*: {sentiment_emoji} _{sentiment}_\n
🎯 *Focus*: {focus}\n
    """
    self.core.telegram.send_message(message)