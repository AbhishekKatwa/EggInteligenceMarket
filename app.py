
from fastapi import FastAPI
from pydantic import BaseModel, Field
import sqlite3, json
from datetime import datetime, timezone
from engine.decision_engine import GodModeEngine

DB="egg_godmode.db"
app=FastAPI(title="Egg God Mode Intelligence Engine",version="17.2")

class AnalyzeRequest(BaseModel):
    market:str
    current_rate:float
    inventory_eggs:int=Field(ge=0)
    messages:list[str]|None=None

class EventRequest(BaseModel):
    timestamp:str
    market:str
    rate:float|None=None
    previous_rate:float|None=None
    change:float|None=None
    direction:str|None=None
    demand_signal:float|None=None
    supply_signal:float|None=None
    sentiment:float|None=None
    confidence:float=.5
    raw_text:str=""

engine=GodModeEngine(DB)

@app.get("/health")
def health():
    return {"status":"ok","engine":"godmode-multi-agent","version":"17.2"}

@app.post("/event")
def event(e:EventRequest):
    con=sqlite3.connect(DB)
    cur=con.cursor()
    cur.execute("""INSERT INTO market_events
      (timestamp,market,event_type,rate,previous_rate,change,direction,
       demand_signal,supply_signal,sentiment,confidence,raw_text)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
      (e.timestamp,e.market,"market_update",e.rate,e.previous_rate,e.change,
       e.direction,e.demand_signal,e.supply_signal,e.sentiment,e.confidence,e.raw_text))
    eid=cur.lastrowid
    con.commit(); con.close()
    return {"event_id":eid}

@app.post("/analyze")
def analyze(r:AnalyzeRequest):
    global engine
    engine=GodModeEngine(DB)
    result=engine.analyze(r.market,r.current_rate,r.inventory_eggs,r.messages)
    con=sqlite3.connect(DB); cur=con.cursor()
    cur.execute("UPDATE recommendations SET status='SUPERSEDED' WHERE market=? AND status='ACTIVE'",(r.market,))
    cur.execute("SELECT id FROM recommendations WHERE market=? ORDER BY id DESC LIMIT 1",(r.market,))
    x=cur.fetchone(); supersedes=x[0] if x else None
    d=result["decision"]
    cur.execute("""INSERT INTO recommendations
      (created_at,market,current_rate,inventory_eggs,action,sell_percent,hold_percent,
       sell_quantity,hold_quantity,confidence,regime,expected_change,evidence_json,supersedes_id)
       VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
      (result["timestamp"],r.market,r.current_rate,r.inventory_eggs,d["action"],
       d["sell_percent"],d["hold_percent"],d["sell_quantity"],d["hold_quantity"],
       result["confidence"],result["regime"],result["forecast"]["expected_change"],
       json.dumps(result["evidence"],ensure_ascii=False),supersedes))
    rid=cur.lastrowid
    con.commit(); con.close()
    result["recommendation_id"]=rid
    return result

@app.get("/recommendations")
def recommendations(market:str|None=None,limit:int=50):
    con=sqlite3.connect(DB); con.row_factory=sqlite3.Row; cur=con.cursor()
    if market: cur.execute("SELECT * FROM recommendations WHERE market=? ORDER BY id DESC LIMIT ?",(market,limit))
    else: cur.execute("SELECT * FROM recommendations ORDER BY id DESC LIMIT ?",(limit,))
    out=[dict(x) for x in cur.fetchall()]
    con.close(); return out
