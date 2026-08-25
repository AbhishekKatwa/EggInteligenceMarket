# Egg God Mode V2 — Inventory-Agnostic Market Brain

This version deliberately removes inventory and quantity from the core intelligence.

## Core question

> Given the information available NOW, what is the market likely to do next?

The engine returns:
- market direction
- 1-day probabilities
- expected move
- market regime
- BUY / SELL / HOLD / WAIT recommendation
- confidence
- risk
- reason codes
- evidence from each agent

## Agents

Market
Crowd Psychology
Supply/Demand
Cross-Market
Regime
Probability
Position/Action
Risk

## Run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Open:
http://127.0.0.1:8000/docs

## Example

POST /analyze

```json
{
  "market": "Barwala",
  "current_rate": 530,
  "messages": [
    "Barwala 530",
    "Delhi down 10",
    "lifting weak",
    "supply tight",
    "market may recover tomorrow"
  ]
}
```

No inventory field exists by design.

## Separate farm economics

A future optional layer can consume this market recommendation and separately calculate farm-specific quantity decisions. It must never feed inventory back into the market forecast.
