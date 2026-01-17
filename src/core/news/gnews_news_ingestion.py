import requests
import os
import json

from datetime import datetime

class GNewsNewsIngestion:
    def __init__(self, core):
        self.core = core
        self.gnews_api_key = os.getenv("GNEWS_API_KEY")
        self.OWNER_ID = os.getenv("OMEGA_OWNER_ID")

    def run(self):
      # Implémentation de l'ingestion des nouvelles depuis GNews
      print("Ingesting news from GNews...")

      news = self.fetch_news()

      print(f"Fetched {len(news)} news articles.")
      print(news[0]['content'])

      if not news:
        print("❌ Pas de news récupérées.")
        return False

      for post in news:
        # Check if news already exists
        existing = self.core.db.execute(
          "SELECT id FROM news_signals WHERE external_id = %s",
          (post['id'],)
        )

        if not existing or len(existing) == 0:
          print(f"Analyse de : {post['title']}")
          analysis = json.loads(self.core.ai.analyze_news(
            title=post['title'],
            description=post['description'],
            content=post['content']
          ))
          print(f"→ Analyse IA: {analysis}")

          if analysis.get('score') > 5:
            self.core.db.execute(
              """
              INSERT INTO news_signals
              (external_id, title, description, content, published_at, url, impact_score, summary_short, sentiment, impact_justification, action_signal, narrative, source_name, user_id)
              VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
              """,
              (
                post['id'],
                post['title'],
                post['description'],
                post['content'],
                post['publishedAt'],
                post['url'],
                analysis['score'],
                analysis['short_summary'],
                analysis['sentiment'],
                analysis['impact_justification'],
                analysis['action_signal'],
                analysis['narrative'],
                "GNews",
                self.OWNER_ID
              )
            )

            if analysis.get('score') > 8:
              self.dispatch_news(post, analysis)
        else:
          print(f"ℹ️ News already exists: {post['title']}")

      return True

    def fetch_news(self):
      # On cherche les news crypto des dernières 24h en français/anglais
      url = f"https://gnews.io/api/v4/search?q=crypto&lang=en&max=10&apikey={self.gnews_api_key}"
      response = requests.get(url, timeout=10)
      if response.status_code == 200:
          return response.json().get("articles", [])
      return []

    def dispatch_news(self, post, analysis):
      emojis_map = {
        "BULLISH": "🟢",
        "BEARISH": "🔴",
        "NEUTRAL": "🟡"
      }

      sentiment_emoji = emojis_map.get(analysis['sentiment'], "⚫")
      """Dispatch high-impact news via Telegram"""
      message = f"""
🚨 *OMEGA INTELLIGENCE - HIGH IMPACT NEWS DETECTED* 🚨

🎯 *Narrative*: {analysis['narrative']}
{sentiment_emoji} *Mood*: _{analysis['sentiment']}_
📓 *Source*: _*GNews*_

📰 *Title*: {post['title']}

📄 *Content*: {post['content']}

📝 *Summary*: {analysis['short_summary']}

⚡ *Impact*: {analysis['impact_justification']}

📈 *Action Signal*: {analysis['action_signal']}

🔗 *Link*: https://cryptopanic.com/news/{post['id']}/{post['slug']}
📅 *Published At*: {datetime.datetime.fromisoformat(post['published_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')}
      """

      self.core.telegram.send_message(message)
