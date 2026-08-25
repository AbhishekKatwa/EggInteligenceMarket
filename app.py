
from fastapi import FastAPI
from pydantic import BaseModel
from engine.market_decision_engine import MarketDecisionEngine

DB = "egg_godmode_market.db"
app = FastAPI(
    title="Egg God Mode — Market Intelligence API",
    version="2.0"
)

engine = MarketDecisionEngine(DB)

class AnalyzeRequest(BaseModel):
    market: str
    current_rate: float
    messages: list[str] = []
    as_of: str | None = None

@app.get("/")
def root():
    return {
        "name": "Egg God Mode",
        "version": "2.0",
        "mode": "inventory-agnostic market intelligence",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "ok",
        "engine": "multi-agent-market-brain",
        "version": "2.0",
        "inventory_agnostic": True
    }

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    global engine
    engine = MarketDecisionEngine(DB)
    result = engine.analyze(
        market=req.market,
        current_rate=req.current_rate,
        messages=req.messages,
        as_of=req.as_of
    )
    result["recommendation_id"] = engine.persist(result)
    return result

@app.get("/recommendations")
def recommendations(market: str | None = None, limit: int = 50):
    import sqlite3
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.cursor()

    if market:
        cur.execute(
            "SELECT * FROM recommendations "
            "WHERE market=? ORDER BY id DESC LIMIT ?",
            (market, limit)
        )
    else:
        cur.execute(
            "SELECT * FROM recommendations ORDER BY id DESC LIMIT ?",
            (limit,)
        )

    result = [dict(x) for x in cur.fetchall()]
    con.close()
    return result
