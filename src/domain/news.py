import os
import requests

class News:
  def __init__(self):
    self.provider = "https://cryptopanic.com/api/developer/v2/posts/"
    self.headers = { 'Accept': 'application/json' }
    self.params = {
      "auth_token": os.getenv("CRYPTOPANIC_API_KEY"),
      "filter": "rising, important",
      # "filter": "rising, hot, bullish, bearish, important",
      "kind": "news",
      "public": "true",
      "metadata": "true",
      "approved": "true",
    }

  def fetch(self):
    try:
      response = requests.get(self.provider, params=self.params, headers=self.headers, timeout=15)

      if response.status_code == 200:
        data = response.json()
        return data
      else:
        print(f"❌ Status {response.status_code}")
        return None

    except Exception as e:
      print(f"🚨 Erreur : {e}")
      return None
