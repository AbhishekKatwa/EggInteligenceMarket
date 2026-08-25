# Egg God Mode V1.2 — Multi-Agent Intelligence Engine

This is the real intelligence layer, not the earlier API skeleton.

## Agents
- Market Agent
- Crowd Psychology Agent
- Supply/Demand Agent
- Cross-Market Agent
- Source Reliability Agent
- Regime Agent
- Probability Agent
- Position Agent
- Risk Agent
- Learning Agent scaffold

## Run
```bash
cd egg_godmode_engine_v1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Swagger: http://127.0.0.1:8000/docs

## Main endpoint
POST `/analyze`

Example:
```json
{
  "market": "Barwala",
  "current_rate": 530,
  "inventory_eggs": 59500,
  "messages": [
    "Barwala 530",
    "lifting weak",
    "Delhi down 10",
    "supply tight"
  ]
}
```

The response contains:
- regime
- probability forecast
- sell/hold allocation
- confidence
- evidence from each agent
- reasoned decision inputs

This is still a research/shadow engine. It does not execute a sale.


## Phase 17 V3 — Historical Replay

Run the historical replay to simulate the engine as information arrived.
The replay is event-driven and can create multiple decisions on the same day.

Outputs:
- `replay/historical_replay_decisions.csv`
- `replay/historical_replay_scored.csv`
- `replay/performance_summary.csv`
- `replay/regime_performance.csv`
- `replay/decision_change_log.csv`
- `replay/replay_report.json`

The score is relative to selling all eggs at the decision-time rate. Carrying cost is assumed to be zero, per the strategy specification.
