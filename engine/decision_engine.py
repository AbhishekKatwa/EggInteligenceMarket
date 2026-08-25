
import sqlite3, json, pandas as pd, numpy as np
from datetime import datetime, timezone
from agents.market_agent import MarketAgent
from agents.crowd_agent import CrowdAgent
from agents.supply_demand_agent import SupplyDemandAgent
from agents.cross_market_agent import CrossMarketAgent
from agents.source_reliability import SourceReliabilityAgent
from agents.regime_agent import RegimeAgent
from agents.probability_agent import ProbabilityAgent
from agents.position_agent import PositionAgent
from agents.risk_agent import RiskAgent

class GodModeEngine:
    def __init__(self, db_path="egg_godmode.db"):
        self.db_path=db_path
        self._load_market_data()
        self.market_agent=MarketAgent(self.daily)
        self.crowd_agent=CrowdAgent()
        self.sd_agent=SupplyDemandAgent()
        self.cross_agent=CrossMarketAgent(self.daily)
        self.source_agent=SourceReliabilityAgent()
        self.regime_agent=RegimeAgent()
        self.prob_agent=ProbabilityAgent(self.daily)
        self.position_agent=PositionAgent()
        self.risk_agent=RiskAgent()

    def _load_market_data(self):
        con=sqlite3.connect(self.db_path)
        # Prefer explicit market_events; fall back to any seeded market observations.
        q="""SELECT timestamp as datetime, market, rate, change FROM market_events
             WHERE market IS NOT NULL AND rate IS NOT NULL"""
        df=pd.read_sql_query(q,con)
        con.close()
        if df.empty:
            self.daily=pd.DataFrame(columns=["date","market","rate","change"])
        else:
            df["datetime"]=pd.to_datetime(df["datetime"],errors="coerce")
            df["date"]=df["datetime"].dt.date
            self.daily=df.sort_values("datetime").groupby(["date","market"],as_index=False).tail(1)
        return self.daily

    def _recent_messages(self, hours=24):
        con=sqlite3.connect(self.db_path)
        q="""SELECT text FROM messages
             WHERE datetime(timestamp) >= datetime('now', ?)
             ORDER BY timestamp DESC"""
        df=pd.read_sql_query(q,con,params=(f"-{hours} hours",))
        con.close()
        return df["text"].tolist() if not df.empty else []

    def analyze(self, market, current_rate, inventory_eggs, messages=None):
        messages=messages if messages is not None else self._recent_messages(24)
        ma=self.market_agent.state(market)
        ca=self.crowd_agent.analyze(messages)
        sa=self.sd_agent.analyze(messages)
        xa=self.cross_agent.analyze(market)
        pa=self.prob_agent.forecast(market)

        regime, regime_conf=self.regime_agent.classify(ca,sa,ma,xa)
        combined_conf=min(.95, np.mean([
            ca["confidence"],sa["confidence"],ma["confidence"],
            xa["confidence"],pa["confidence"],regime_conf
        ]))
        decision=self.position_agent.decide(regime,pa["confidence"],inventory_eggs)
        conflict=(regime=="CONFLICTED")
        decision=self.risk_agent.apply(decision,combined_conf,conflict)

        evidence={
            "market_agent":ma,"crowd_agent":ca,"supply_demand_agent":sa,
            "cross_market_agent":xa,"probability_agent":pa,
            "regime_confidence":regime_conf
        }
        return {
            "timestamp":datetime.now(timezone.utc).isoformat(),
            "market":market,"current_rate":current_rate,
            "inventory_eggs":inventory_eggs,"regime":regime,
            "confidence":combined_conf,"forecast":pa,
            "decision":decision,"evidence":evidence
        }
