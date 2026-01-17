import json
import os
from groq import Groq
import time

class AI:
  def __init__(self):
    self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    self.model = "llama-3.3-70b-versatile"
    self.available_models = ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "deepseek-r1-distill-llama-70b"]
    self.current_model_index = 0

  def _get_next_model(self):
    """Rotate to the next available model"""
    self.current_model_index = (self.current_model_index + 1) % len(self.available_models)
    self.model = self.available_models[self.current_model_index]
    print(f"🔄 Switching to model: {self.model}")
    return self.model

  def _make_request_with_fallback(self, messages, max_retries=3):
    """Make a request with automatic fallback to other models if rate limited"""
    attempts = 0
    last_error = None

    while attempts < max_retries:
      try:
        chat_completion = self.client.chat.completions.create(
          messages=messages,
          model=self.model,
          response_format={ "type": "json_object" }
        )
        return chat_completion.choices[0].message.content

      except Exception as e:
        last_error = e
        error_message = str(e).lower()

        # Check if it's a rate limit error
        if "rate" in error_message or "limit" in error_message or "429" in error_message:
          attempts += 1
          print(f"⚠️ Rate limit reached on {self.model}. Attempt {attempts}/{max_retries}")

          if attempts < max_retries:
            # Try next model
            self._get_next_model()
            time.sleep(1)  # Brief delay before retry
          else:
            print(f"❌ All models exhausted after {max_retries} attempts")
            raise Exception(f"Rate limit exceeded on all available models: {last_error}")
        else:
          # For other errors, raise immediately
          print(f"❌ API Error: {e}")
          raise e

    raise Exception(f"Failed after {max_retries} attempts: {last_error}")

  def analyze_news(self, title, description, content=None):
    prompt = f"""
      Tu es un analyste quantitatif senior chez un fonds spéculatif crypto.
      Ton objectif est d'aider à accumuler du BTC en identifiant les signaux forts dans le bruit médiatique.

      DONNÉES :
      TITRE : <#title#>
      DESCRIPTION : <#description#>
      CONTENT: <#content#>

      INSTRUCTIONS DE SCORING (1-10) :
      - 1-3 : Bruit. News de remplissage, rumeurs non vérifiées, analyses techniques mineures.
      - 4-6 : Signaux de Momentum. Adoption réelle, records de transactions (ex: ton record d'ETH), achats institutionnels modérés.
      - 7-9 : Changements Structurels. Approbations réglementaires, investissements de plus de 100M$, percées technologiques majeures.
      - 10 : Événements Systémiques. Black Swan ou annonces type "Halving/ETF".

      FORMAT DE SORTIE JSON UNIQUEMENT :
      {{
          "score": int,
          "sentiment": "BULLISH" | "BEARISH" | "NEUTRAL",
          "narrative": "L1" | "AI" | "RWA" | "MACRO" | "MEME" | "BITCOIN",
          "key_target": float | null,
          "short_summary": "Résumé ultra-condensé de la news en 10 mots max.",
          "impact_justification": "Explique pourquoi ce score. Quel est l'enjeu réel pour la liquidité ou le prix ?",
          "action_signal": "Conseil rapide (ex: 'Surveiller la résistance', 'Accumulation institutionnelle', 'Ignore le bruit')"
      }}
    """
    prompt_filled = prompt.replace("<#title#>", title).replace("<#description#>", description or "N/A").replace("<#content#>", content or "N/A")

    messages = [{"role": "user", "content": prompt_filled}]
    return self._make_request_with_fallback(messages)

  def analyze_market(self, news):
    titles = [n['title'] for n in news]
    prompt = f"""
      En tant qu'expert Macro & Crypto, analyse la situation au 05/01/2026.
      News récentes : {titles}

      Tâche :
      1. Analyse rapidement le marché crypto en direct, les dernieres news ou tendances.
      2. Identifie les événements macro US / Europe ou Asie les plus proches (ex: Minutes de la Fed, Chômage).
      3. Identifie le/les narratifs en vogue du moment (ex: RWA, IA, DEPIN, Layer 1, Layer 2, etc..) et analyse les mouvements de fonds pour anticiper des transitioms entre narratifs ou blockchains.
      4. Rédige un 'Executive Brief' de 5 phrases maximum pour mon dashboard.
      5. Détermine le sentiment dominant (BULLISH/BEARISH/CAUTIOUS).

      Réponds au format JSON : {{"brief": "...", "sentiment": "...", "focus": "..."}}
    """

    messages = [{"role": "user", "content": prompt}]
    return self._make_request_with_fallback(messages)

  def analyze_portfolio(self, portfolio_data):
    PROMPT_RESPONSE = {
      "summary": "string",
      "risk_score": "int",
      "narrative_score": "int",
      "velocity_score": "int",
      "btc_accumulation_index": "int",
    }

    # CONSTRUCTION DU MASTER PROMPT OPTIMISÉ
    prompt = f"""
    SYSTEM ROLE: Tu es le Chief Investment Officer (CIO) d'un fonds crypto Hedge Fund.
    Ton objectif : Atteindre 1M€ d'ici 2035 pour ce client.
    Ton style : Froid, analytique, pragmatique. Pas de complaisance.

    DATA DU PORTEFEUILLE:
    - Valeur Totale: {portfolio_data['total_value']} USD
    - Assets: {portfolio_data['assets']}
    - Contexte Marché: {portfolio_data['market_context']}

    INSTRUCTIONS D'ANALYSE EN DEUX POINTS:

    PARTIE 1 : AUDIT INTERNE (Mouvements & Structure)
    - Analyse l'allocation : Es-tu trop exposé à un narratif spécifique ?
    - Analyse la "Distance à la Target" : Quels assets sont proches du Take Profit ?
    - Calcule l'efficience : Le risque pris sur les Altcoins est-il récompensé par rapport à une détention 100% BTC ?

    PARTIE 2 : ANALYSE EXTERNE (Narratifs & Marché)
    - Aligne les assets du client avec les narratifs de 2026 (IA, RWA, L1 high-speed, DePIN).
    - Identifie les "poids morts" : Assets dont le narratif s'essouffle ou qui sous-performent le marché.
    - Analyse de cycle : En ce début 2026, est-ce le moment d'accumuler ou de dé-risquer vers le BTC ?

    SORTIE ATTENDUE:
    AUDIT DE STRUCTURE (Tes conclusions sur l'équilibre du wallet)

    RADAR DE MARCHÉ & NARRATIFS (Positionnement par rapport aux tendances actuelles)

    ## ⚡ ACTIONS IMMÉDIATES (STRATÉGIE 2035)
    - [ ] VENDRE / ALLÉGER : (Quel asset et pourquoi)
    - [ ] ACCUMULER : (Quel asset et pourquoi)
    - [ ] REBALANCER : (Mouvement vers BTC pour le socle long terme)

    INSTRUCTIONS DE SCORING (Chaque score doit être motivé) :
    1. "risk_score": (0=Sécurisé/BTC, 100=Degenerate/Alts)
    2. "narrative_score": (0=Obsolète, 100=Tendances 2026)
    3. "velocity_score": (Proximité trajectoire 1M€ 2035)
    4. "btc_accumulation_index": (Efficacité de la conversion des profits vers BTC)

    tu concluras ton analyse par ces scores.

    reponds sous la forme d'un text de la longueur suffisante pour couvrir tous les points demandés .
    """
    user_content = f"Génère l'analyse stratégique de ce portefeuille au format json : {PROMPT_RESPONSE}"

    messages = [
      {"role": "system", "content": prompt},
      {"role": "user", "content": user_content}
    ]
    return self._make_request_with_fallback(messages)

  def generate_flash_brief(self, data):
    PROMPT_RESPONSE = {
      "brief": "string",
      "recommendation": "string",
      "global_mood": "string"
    }
    flash_prompt = f"""
    SYSTEM ROLE:
    Tu es une sentinelle de marché crypto. Ton rôle est de faire un briefing flash de 4 à 5 phrases maximum. 
    Style : Froid, direct, sans salutations. Focus sur l'efficacité stratégique.

    DONNÉES DU JOUR :
    - Valeur totale du portefeuille : {data['total_val']} USD
    - Top Performer : {data['top_performer']['symbol']} ({data['top_performer'].get('change_24h', 0)}%)
    - Worst Performer : {data['worst_performer']['symbol']} ({data['worst_performer'].get('change_24h', 0)}%)
    - Performance BTC 24h : {data['btc_change']}%

    INSTRUCTIONS :
    1. Évalue la santé immédiate du portefeuille par rapport au BTC.
    2. Identifie si le mouvement du jour est une opportunité ou un risque.
    3. Rappelle la direction vers l'objectif 1M€ en 2035.
    4. Finis par une recommandation d'une phrase (sujet: Hold, Trim, ou Accumulate).
    5. Détermine le "global_mood" du portefeuille (BULLISH, BEARISH, NEUTRAL).

    FORMAT : Texte brut, 5 phrases maximum. Utilise ce JSON: {PROMPT_RESPONSE}.
    """
    messages = [{"role": "user", "content": flash_prompt}]
    return self._make_request_with_fallback(messages)

  def analyze_stocks_portfolio(self, portfolio_data):
    PROMPT_RESPONSE = {
      "summary": "string",
    }
    system_prompt = f"""
    RÔLE : Expert en Ingénierie Financière.
    MISSION : Analyser un portefeuille multi-piliers (Accumulation Long Terme).

    Piliers : 1 (ETF Fondations), 2 (Stocks Performance), 3 (Accélérateurs/Pépites).

    LOGIQUE D'ANALYSE :
    1. Check des corrélations (ex: trop de crypto-proxies vs ETF).
    2. Détection des dérives de poids entre les 3 piliers.
    3. Suggestion d'actions ou ETFS pour DCA (300-400€) pour optimiser l'effet composé.

    REPONDS EN FRANÇAIS. Style direct, concis, technique. Pas de blabla. tu peux proposer des conseils d'optomisation de gestion
    pour repondre utilise ce format JSON : {PROMPT_RESPONSE}.
    je veux un text de 10 phrases maximum dans le champs 'summary'.
    """

    user_content = f"Voici mon portefeuille actuel : {json.dumps(portfolio_data, indent=2)}"
    messages = [
      {"role": "system", "content": system_prompt},
      {"role": "user", "content": user_content}
    ]
    return self._make_request_with_fallback(messages)
