# 📁 OMEGA Intelligence Core — The Wealth Intelligence Engine

[![Docker Support](https://img.shields.io/badge/Docker-Supported-blue.svg?logo=docker)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.11](https://img.shields.io/badge/Python-3.11-green.svg?logo=python)](https://www.python.org/)

**OMEGA-Core** is the analytical engine of the OMEGA Intelligence suite. It orchestrates data ingestion (Crypto, Stocks, News), automates wealth snapshots, and generates predictive insights using Artificial Intelligence.

Designed to run 24/7 on lightweight infrastructure (Raspberry Pi, NAS, VPS), it serves as the mathematical guardian of your financial trajectory toward 2035.



## 🧱 Mandatory Prerequisites (Cloud)
Before launching the Engine, you must have an operational OMEGA-Cloud instance. If you haven't configured your database yet: 👉 [Visit the OMEGA-Cloud repository](https://github.com/omega-intelligence-suite/omega-cloud) to initialize your SQL schema.



## 🚀 Quick Start (Installation)

The installation is fully automated to ensure maximum stability on any Linux system (ARM or x86).

```bash
# 1. Clone the repository
git clone https://github.com/omega-intelligence-suite/omega-core.git
cd omega-core

# 2. Make the setup script executable
chmod +x setup.sh

# 3. Launch the installation wizard
./setup.sh
```



## 🛠 What the Setup Wizard Does
The setup.sh script handles all the heavy lifting:

1. **Prerequisites Check**: Verifies the presence of Docker and Docker Compose.

2. **Environment Config**: Guides you through configuring your Supabase and Groq keys without ever touching the source code.

3. **Storage Setup**: Prepares persistent log volumes.

4. **Containerization**: Builds the optimized Docker image and launches the service in "detached" mode (background).





## 📅 Scheduling (Engine Heartbeat)
Once launched, the Engine follows a strict schedule defined in scheduler.py:

| Fequency | Task | Description |
| --- | --- | --- |
| Every 10 minutes | assets:prices_sync | Real-time price updates (Yahoo Finance / CoinGecko) |
| Every 15 minutes | news:finnhub | Macro-economic news stream ingestion (Macro + Crypto) |
| Every 30 minutes | news:gnews | Crypto specific news stream ingestion |
| Every 1 hour | wallet:sync | Live balance synchronization (Binance) |
| Every 1 hour | intelligence:flash_brief | AI Flash Brief generation |
| Every 8 hours | news:cryptopanic | Crypto specific news stream ingestion |
| 06:00 AM | intelligence:market | AI Market Intelligence generation |
| 06:00 AM | intelligence:wallet | AI Wallet Intelligence generation |
| 06:00 AM | intelligence:stocks | AI Stocks Intelligence generation |
| 11:50 PM | wallet:snapshot | AI Wallet Intelligence generation |




## 🐳 Container Management
The engine runs within a Docker container named omega-core. Here are the essential commands:

- **Monitor live activity**
```bash
docker logs -f omega-core
```

- **Restart the container**
```bash
docker restart omega-core
```

- **Stop the container**
```bash
docker stop omega-core
```

- **Start the container**
```bash
docker start omega-core
```

- **Remove the container**
```bash
docker rm omega-core
```



## 🔒 Security & Privacy

- **Self-Hosted**: Your API keys and credentials never leave your machine.

- **Isolated**: The Docker container sandboxes the engine from the rest of your system.

- **Stateless**: The Engine does not store data locally; everything is secured within your own Supabase instance via Row Level Security (RLS) policies.

