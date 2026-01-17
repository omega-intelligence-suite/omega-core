import requests
import os
import json
from datetime import datetime, timezone

class FinnhubNewsIngestion:
  def __init__(self, core):
    self.core = core
    self.finnhub_api_key = os.getenv("FINNHUB_API_KEY")
    self.OWNER_ID = os.getenv("OMEGA_OWNER_ID")
    self.macro_focus_keywords = [
      "stock market",
      "economy",
      "inflation",
      "interest rates",
      "earnings",
      "recession",
      "unemployment",
      "federal reserve",
      "monetary policy",
      "financial markets",
      "investment",
      "trading",
      "market volatility",
      "GDP",
      "consumer confidence",
      "bce",
      "nasdaq",
      "dow jones",
      "s&p 500",
    ]

  def run(self):
    self._run_macro_news()
    self._run_crypto_news()

    return True

  def _run_crypto_news(self):
    news_data = self._fetch_news(category="crypto")
    print(f"✅ {len(news_data)} news CRYPTO récupérées.")

    for news in news_data[:10]:

      existing = self.core.db.execute(
        "SELECT id FROM news_signals WHERE external_id = %s",
        (str(news['id']),)
      )
      if not existing or len(existing) == 0:
        headline = news.get('headline', '')
        summary = news.get('summary', '')

        print(f"Analyse de : {headline}")
        analysis = json.loads(self.core.ai.analyze_news(
          title=headline,
          description=summary
        ))
        print(f"→ Analyse IA: {analysis}")

        if analysis.get('score') > 5:
          self.core.db.execute(
            """
            INSERT INTO news_signals
            (external_id, title, description, content, published_at, url, impact_score, summary_short, sentiment, impact_justification, action_signal, narrative, source_name, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
              str(news['id']),
              news['headline'],
              news['summary'],
              news['summary'],
              datetime.fromtimestamp(news['datetime'], tz=timezone.utc),
              news['url'],
              analysis['score'],
              analysis['short_summary'],
              analysis['sentiment'],
              analysis['impact_justification'],
              analysis['action_signal'],
              analysis['narrative'],
              "Finnhub_Crypto",
              self.OWNER_ID
            )
          )

          print('Insert macro news signal into database.')
      else:
        print(f"ℹ️ News already exists: {news['headline']}")

    return True


  def _run_macro_news(self):
    news_data = self._fetch_news(category="top")
    print(f"✅ {len(news_data)} news macro récupérées.")

    market_digest = []
    for news in news_data:
      existing = self.core.db.execute(
        "SELECT id FROM news_signals WHERE external_id = %s",
        (str(news['id']),)
      )

      if not existing or len(existing) == 0:
        headline = news.get('headline', '')
        summary = news.get('summary', '')

        if len(market_digest) <= 10:
          if any(key.lower() in (headline + summary).lower() for key in self.macro_focus_keywords):
            market_digest.append({
              "title": news['headline'],
              "url": news['url'],
              "summary": news['summary'],
              "publishedAt": news['datetime'],
              "id": news['id'],
            })

    print("✅ Market Digest filtered news count:", len(market_digest))

    try:
      for post in market_digest:
        print('Insert macro news signal into database.')
        print(f"Analyse de : {datetime.fromtimestamp(post['publishedAt'], tz=timezone.utc)}")
        analysis = json.loads(self.core.ai.analyze_news(
          title=post['title'],
          description=post['summary'],
          content=post['summary']
        ))
        print(f"→ Analyse IA: {analysis}")

        if analysis.get('score') > 5:
          self.core.db.execute(
            """
            INSERT INTO news_signals
            (external_id, title, description, content, published_at, url, impact_score, summary_short, sentiment, impact_justification, action_signal, narrative, source_name, user_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
              str(post['id']),
              post['title'],
              post['summary'],
              post['summary'],
              datetime.fromtimestamp(post['publishedAt'], tz=timezone.utc),
              post['url'],
              analysis['score'],
              analysis['short_summary'],
              analysis['sentiment'],
              analysis['impact_justification'],
              analysis['action_signal'],
              analysis['narrative'],
              "Finnhub",
              self.OWNER_ID
            )
          )

          print('Insert macro news signal into database.')
    except Exception as e:
      print(f"🚨 Erreur lors de l'insertion des news macro : {e}")
      # if analysis.get('score') > 8:
        # self.dispatch_news(post, analysis)

  def _fetch_news(self, category="top"):
    url = f"https://finnhub.io/api/v1/news?category={category}&token={self.finnhub_api_key}"
    response = requests.get(url, timeout=15)

    return response.json()