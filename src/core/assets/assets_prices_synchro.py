import os
import requests
import time

class AssetsPriceSynchro:
  def __init__(self, core):
    self.coingecko_api_key = os.getenv("COINGECKO_API_KEY")
    self.core = core

  def _fetch_yahoo_finance_direct(self, symbol):
    """
    Fetch stock data directly from Yahoo Finance API v8
    """
    try:
      url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
      params = {
        'range': '5d',
        'interval': '1d',
        'includePrePost': 'false'
      }

      headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
      }

      response = requests.get(url, params=params, headers=headers, timeout=10)

      if response.status_code != 200:
        return None

      data = response.json()

      # Extract price data
      if 'chart' not in data or 'result' not in data['chart']:
        return None

      result = data['chart']['result']
      if not result or len(result) == 0:
        return None

      quote = result[0]

      if 'timestamp' not in quote or 'indicators' not in quote:
        return None

      timestamps = quote['timestamp']
      quotes = quote['indicators']['quote'][0]

      if not timestamps or 'close' not in quotes:
        return None

      closes = quotes['close']

      # Filter out None values
      prices = []
      for i, close in enumerate(closes):
        if close is not None:
          prices.append(close)

      return prices if len(prices) >= 2 else None

    except Exception as e:
      print(f"  ⚠️ API error for {symbol}: {str(e)[:50]}")
      return None

  def run(self):
    print("🔄 Début de la mise à jour des prix...")
    my_assets = self.core.db.execute("SELECT id, name, symbol, type, change_24h FROM user_assets WHERE type != 'BANK'")

    stock_symbols = [asset['symbol'] for asset in my_assets if asset['type'] == 'STOCKS_ETFS']

    # Fetch crypto prices from CoinGecko
    headers = {
      "accept": "application/json",
      "x-cg-demo-api-key": self.coingecko_api_key
    }
    url = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page=1&sparkline=false&price_change_percentage=24h"
    coingecko_data = requests.get(url, headers=headers, timeout=10).json()

    # Fetch stock prices from Yahoo Finance
    stock_data_cache = {}
    if stock_symbols:
      print(f"📊 Fetching data for {len(stock_symbols)} stocks: {stock_symbols}")

      for i, symbol in enumerate(stock_symbols, 1):
        try:
          print(f"\n🔍 [{i}/{len(stock_symbols)}] Processing {symbol}...")

          prices = self._fetch_yahoo_finance_direct(symbol)

          if prices and len(prices) >= 2:
            stock_data_cache[symbol] = prices
            print(f"  ✅ {symbol}: {len(prices)} days, latest: ${prices[-1]:.2f}")
          else:
            print(f"  ❌ {symbol}: No data available")

          # Rate limiting delay
          if i < len(stock_symbols):
            time.sleep(1)

        except Exception as e:
          print(f"  ❌ {symbol}: {str(e)[:100]}")
          continue

    # Update all assets in database
    for asset in my_assets:
      current_price = None
      change_24h = None

      if asset['type'] == 'CRYPTO':
        [current_price, change_24h] = self._get_crypto_prices(asset['symbol'], coingecko_data)
      elif asset['type'] == 'STOCKS_ETFS':
        [current_price, change_24h] = self._get_stock_prices(asset['symbol'], stock_data_cache)

      if current_price is not None and change_24h is not None:
        self.core.db.execute(
          """UPDATE user_assets
              SET current_price = %s, change_24h = %s, last_price_sync_at = NOW()
              WHERE id = %s""",
          (current_price, change_24h, asset['id']))

      if current_price is not None:
        print(f"✅ {asset['symbol']}: ${current_price} ({change_24h:+.2f}%)")

        # Alert on 5%+ price changes
        if asset['change_24h'] is not None and change_24h is not None:
          change_diff = abs(change_24h - asset['change_24h'])
          if change_diff >= 5:
            direction = "📈" if change_24h > asset['change_24h'] else "📉"
            message = f"{direction} {asset['name']} ({asset['symbol'].upper()})\nPrice: ${current_price}\n24h Change: {change_24h:+.2f}%"
            self.core.telegram.send_message(message)
      else:
        print(f"⚠️ Prix non trouvé pour {asset['symbol']}")

    print(f"\n✅ Successfully updated {len(my_assets)} assets")
    return True


  def _get_crypto_prices(self, symbol, coingecko_data):
    """Extract crypto prices from CoinGecko data"""
    token = symbol.lower()
    coingecko_token = next((item for item in coingecko_data if item.get('symbol') == token), None)

    if coingecko_token:
      return [coingecko_token['current_price'], coingecko_token['price_change_percentage_24h']]

    return [None, None]

  def _get_stock_prices(self, symbol, stock_data_cache):
    """Calculate current price and 24h change from cached stock data"""
    try:
      if symbol not in stock_data_cache:
        return [None, None]

      prices = stock_data_cache[symbol]

      if len(prices) < 2:
        return [prices[0], None] if len(prices) == 1 else [None, None]

      current_price = prices[-1]
      previous_price = prices[-2]
      change_24h = ((current_price - previous_price) / previous_price) * 100

      return [current_price, change_24h]

    except Exception as e:
      print(f"  ⚠️ Error processing {symbol}: {e}")
      return [None, None]