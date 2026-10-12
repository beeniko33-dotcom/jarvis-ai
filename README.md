# Jarvis AI

Backend bridge, risk management, adaptive trading bot components, and supporting services for the Jarvis ecosystem.

## Key Components

| File / Folder | Description |
|---------------|-------------|
| `jarvis_ai.py` | Core AI / agent logic |
| `adaptive_ai_trading_bot.py` | Adaptive trading bot |
| `risk_manager.py` / `risk_server.py` | Risk management layer |
| `backtest_engine.py` | Backtesting utilities |
| `docker-compose.yml` + Dockerfiles | Container orchestration |
| `frontend/` | Frontend assets |
| `plugins/` | Plugin system |
| `tests/` | Test suite |

## Quick Start

```bash
# Clone
git clone https://github.com/beeniko33-dotcom/jarvis-ai.git
cd jarvis-ai

# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure (create .env from any available examples)
# Then run the desired entry point, e.g.:
# python jarvis_ai.py
# or via docker-compose
```

## Related Repositories

- **Main trading bot**: [jarvis-trader-ecosystem](https://github.com/beeniko33-dotcom/jarvis-trader-ecosystem)
- Other experimental / satellite projects exist under the same account.

## Notes

- A SQLite `risk.db` file was previously committed and has been removed. Databases should be generated at runtime or stored outside the repository.
- Keep all secrets in `.env` files that are listed in `.gitignore`.
- This repository contains experimental components. Treat as research code.

## Status

Active development / experimental. Prefer the main `jarvis-trader-ecosystem` repository for the primary Telegram + ML trading bot experience.
