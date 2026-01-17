#!/bin/bash

GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}=========================================="
echo -e "   OMEGA CORE - Setup Wizard"
echo -e "==========================================${NC}\n"

# 1. Vérification des pré-requis
echo -e "🔍 Checking prerequisites..."
if ! [ -x "$(command -v docker)" ]; then
  echo -e "${RED}Error: Docker is not installed.${NC}" >&2
  exit 1
fi

if ! [ -x "$(command -v docker-compose)" ] && ! docker compose version >/dev/null 2>&1; then
  echo -e "${RED}Error: Docker Compose is not installed.${NC}" >&2
  exit 1
fi
echo -e "${GREEN}✅ Docker and Docker Compose are ready.${NC}\n"

# 2. Configuration du fichier .env
if [ -f .env ]; then
    echo -e "${BLUE}⚠️  An .env file already exists.${NC}"
    read -p "Do you want to overwrite it? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        SKIP_ENV=true
    fi
fi

if [ "$SKIP_ENV" != true ]; then
    echo -e "⚙️  Configuring environment variables..."

    read -p "Enter Supabase URL: " sb_url
    read -p "Enter Supabase Service Role Key: " sb_key
    read -p "Enter Supabase DB Host: " sb_db_host
    read -p "Enter Supabase DB Port: " sb_db_port
    read -p "Enter Supabase DB Name: " sb_db_name
    read -p "Enter Supabase DB User: " sb_db_user
    read -p "Enter Supabase DB Password: " sb_db_password

    read -p "Enter OMEGA Owner ID: " omega_owner_id

    read -p "Enter Groq API Key: " groq_key

    read -p "Enter GNews API Key: " gnews_key
    read -p "Enter Finnhub API Key: " finnhub_key
    read -p "Enter CryptoPanic API Key: " cp_key

    read -p "Enter CoinGecko API Key: " cg_key

    read -p "Enter Telegram Bot Token (optional): " tg_token
    read -p "Enter Telegram Chat ID (optional): " tg_id

    read -p "Enter Binance API Key: " binance_key
    read -p "Enter Binance API Secret: " binance_secret

    cat <<EOF > .env
# OMEGA CONFIG
SUPABASE_URL=$sb_url
SUPABASE_KEY=$sb_key
SUPABASE_DB_HOST=$sb_db_host
SUPABASE_DB_PORT=$sb_db_port
SUPABASE_DB_NAME=$sb_db_name
SUPABASE_DB_USER=$sb_db_user
SUPABASE_DB_PASSWORD=$sb_db_password

# AI CONFIG
GROQ_API_KEY=$groq_key

# NOTIFICATIONS
TELEGRAM_BOT_TOKEN=$tg_token
TELEGRAM_CHAT_ID=$tg_id

# EXCHANGES
BINANCE_API_KEY=$binance_key
BINANCE_API_SECRET=$binance_secret

# NEWS
CRYPTOPANIC_API_KEY=$cp_key
GNEWS_API_KEY=$gnews_key
FINNHUB_API_KEY=$finnhub_key

# COINGECKO
COINGECKO_API_KEY=$cg_key

# OMEGA
OMEGA_OWNER_ID=$omega_owner_id
EOF
    echo -e "${GREEN}✅ .env file created.${NC}\n"
fi

# 3. Création des répertoires nécessaires
echo -e "📁 Creating local directories..."
mkdir -p logs
echo -e "${GREEN}✅ Directories created.${NC}\n"

# 4. Build et Lancement
echo -e "🚀 Building and starting OMEGA Core..."
docker compose up -d --build

echo -e "\n${GREEN}=========================================="
echo -e "   SETUP COMPLETED SUCCESSFULLY"
echo -e "==========================================${NC}"
echo -e "Your OMEGA Engine is now running in the background."
echo -e "To see logs, run: ${BLUE}docker logs -f omega-core${NC}"