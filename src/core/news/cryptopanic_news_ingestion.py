import datetime
import json

from src.domain.news import News
from src.domain.ai import AI

class CryptoPanicNewsIngestion:
  def __init__(self, core):
    self.core = core

  def run(self):
    news = self.fetch_news()
    if not news:
      print("❌ Pas de news récupérées.")
      return False

    for post in news['results']:
      # Check if news already exists
      existing = self.core.db.execute(
        "SELECT id FROM news_signals WHERE external_id = %s", 
        (str(post['id']),)
      )

      if not existing or len(existing) == 0:
        print(f"Analyse de : {post['title']}")
        analysis = self.process_news_with_ai(post)

        print(f"→ Analyse IA: {analysis}")

        self.aggregate_news_data(post, analysis)
        if analysis.get('impact_score') > 8:
          self.dispatch_news(post, analysis)
      else:
        print(f"ℹ️ News already exists: {post['title']}")

    return True


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
📓 *Source*: _*CryptoPanic*_

📰 *Title*: {post['title']}

📝 *Summary*: {analysis['short_summary']}

⚡ *Impact*: {analysis['impact_justification']}

📈 *Action Signal*: {analysis['action_signal']}

🔗 *Link*: https://cryptopanic.com/news/{post['id']}/{post['slug']}
📅 *Published At*: {datetime.datetime.fromisoformat(post['published_at'].replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S')}
    """

    self.core.telegram.send_message(message)


  def fetch_news(self):
    news_provider = News()
    news = news_provider.fetch()

    if not news:
      print("❌ Pas de news récupérées.")
    else:
      print(f"✅ {len(news['results'])} news récupérées.")

    return news


  def process_news_with_ai(self, news):
    analysis = self.core.ai.analyze_news(title=news.get('title', ''), description=news.get('description', ''))
    return json.loads(analysis)


  def aggregate_news_data(self, post, analysis):
    if analysis['score'] > 6:
      self.core.db.execute("""
        INSERT INTO news_signals
        (external_id, title, description, url, source_name, currencies, impact_score, summary_short, sentiment, published_at, impact_justification, action_signal, narrative, source_name)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
      """, (
        str(post['id']),
        post['title'],
        post['description'],
        'https://cryptopanic.com/news/' + str(post['id']) + "/" + post['slug'],
        "",
        [],
        analysis['score'],
        analysis['short_summary'],
        analysis['sentiment'],
        post['published_at'],
        analysis['impact_justification'],
        analysis['action_signal'],
        analysis['narrative'],
        "CryptoPanic"
      ))

      self.core.db.connection.commit()
    return True