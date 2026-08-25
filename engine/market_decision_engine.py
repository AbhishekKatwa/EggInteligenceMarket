
import sqlite3, json
from datetime import datetime, timezone
import numpy as np
import pandas as pd

from agents.market_agent import MarketAgent
from agents.crowd_agent import CrowdAgent
from agents.supply_demand_agent import SupplyDemandAgent
from agents.cross_market_agent import CrossMarketAgent
from agents.regime_agent import RegimeAgent
from agents.probability_agent import ProbabilityAgent
from agents.position_agent import PositionAgent
from agents.risk_agent import RiskAgent

class MarketDecisionEngine:
    """
    Inventory-agnostic God Mode market brain.

    Input:
        market + current rate + evidence/messages

    Output:
        direction, probabilities, expected move, regime, confidence,
        action (BUY/SELL/HOLD/WAIT), risk and evidence.

    It never receives or uses inventory.
    """

    def __init__(self, db_path="egg_godmode_market.db"):
        self.db_path = db_path
        self._load_market_data()
        self.market_agent = MarketAgent(self.daily)
        self.crowd_agent = CrowdAgent()
        self.sd_agent = SupplyDemandAgent()
        self.cross_agent = CrossMarketAgent(self.daily)
        self.regime_agent = RegimeAgent()
        self.prob_agent = ProbabilityAgent(self.daily)
        self.position_agent = PositionAgent()
        self.risk_agent = RiskAgent()

    def _load_market_data(self):
        con = sqlite3.connect(self.db_path)
        df = pd.read_sql_query(
            "SELECT timestamp AS datetime, market, rate, change FROM market_events "
            "WHERE market IS NOT NULL AND rate IS NOT NULL",
            con
        )
        con.close()

        if df.empty:
            self.daily = pd.DataFrame(columns=["date","market","rate","change"])
            return

        df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
        df["date"] = df["datetime"].dt.date
        self.daily = (
            df.sort_values("datetime")
              .groupby(["date","market"], as_index=False)
              .tail(1)
        )

    def analyze(self, market, current_rate, messages=None, as_of=None):
        messages = messages or []

        ma = self.market_agent.state(market)
        ca = self.crowd_agent.analyze(messages)
        sa = self.sd_agent.analyze(messages)
        xa = self.cross_agent.analyze(market)
        pa = self.prob_agent.forecast(market, as_of=as_of)

        regime, regime_conf = self.regime_agent.classify(
            ca, sa, ma, xa
        )

        confidence = float(min(.95, np.mean([
            ca["confidence"],
            sa["confidence"],
            ma["confidence"],
            xa["confidence"],
            pa["confidence"],
            regime_conf
        ])))

        source_conflict = regime == "CONFLICTED"
        risk = self.risk_agent.assess(
            confidence, pa["p_up"], pa["p_down"], source_conflict
        )

        decision = self.position_agent.decide(
            regime,
            pa["p_up"],
            pa["p_down"],
            confidence,
            pa["expected_change"]
        )

        direction = (
            "UP" if pa["p_up"] > pa["p_down"] and pa["p_up"] >= pa["p_flat"]
            else "DOWN" if pa["p_down"] > pa["p_up"] and pa["p_down"] >= pa["p_flat"]
            else "FLAT"
        )

        reason_codes = []
        if ca["fear"] >= 75:
            reason_codes.append("EXTREME_CROWD_FEAR")
        if ca["sentiment"] >= 75:
            reason_codes.append("CROWD_EUPHORIA")
        if sa["supply_tightness"] >= 65:
            reason_codes.append("SUPPLY_TIGHT")
        if sa["supply_tightness"] <= 35:
            reason_codes.append("SUPPLY_LOOSE")
        if sa["demand"] >= 65:
            reason_codes.append("DEMAND_STRONG")
        if sa["demand"] <= 35:
            reason_codes.append("DEMAND_WEAK")
        if xa["signal"] >= 65:
            reason_codes.append("REGIONAL_BREADTH_POSITIVE")
        if xa["signal"] <= 35:
            reason_codes.append("REGIONAL_BREADTH_NEGATIVE")
        if source_conflict:
            reason_codes.append("SIGNAL_CONFLICT")

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "market": market,
            "current_rate": current_rate,
            "regime": regime,
            "direction": direction,
            "probability": {
                "1d_up": pa["p_up"],
                "1d_flat": pa["p_flat"],
                "1d_down": pa["p_down"]
            },
            "expected_move_1d": pa["expected_change"],
            "confidence": confidence,
            "recommendation": decision["action"],
            "risk": risk["risk"],
            "horizon": "1D",
            "reason_codes": reason_codes,
            "evidence": {
                "market": ma,
                "crowd": ca,
                "supply_demand": sa,
                "cross_market": xa,
                "probability": pa,
                "regime_confidence": regime_conf,
                "risk_flags": risk["risk_flags"]
            }
        }

    def persist(self, result):
        con = sqlite3.connect(self.db_path)
        cur = con.cursor()

        cur.execute(
            "UPDATE recommendations SET status='SUPERSEDED' "
            "WHERE market=? AND status='ACTIVE'",
            (result["market"],)
        )
        cur.execute(
            "SELECT id FROM recommendations WHERE market=? "
            "ORDER BY id DESC LIMIT 1",
            (result["market"],)
        )
        old = cur.fetchone()
        supersedes = old[0] if old else None

        p = result["probability"]
        cur.execute("""
            INSERT INTO recommendations
            (created_at,market,current_rate,direction,regime,p_up,p_flat,p_down,
             expected_change_1d,confidence,action,risk,horizon,reason_codes_json,
             evidence_json,supersedes_id)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            result["timestamp"], result["market"], result["current_rate"],
            result["direction"], result["regime"], p["1d_up"], p["1d_flat"],
            p["1d_down"], result["expected_move_1d"], result["confidence"],
            result["recommendation"], result["risk"], result["horizon"],
            json.dumps(result["reason_codes"]),
            json.dumps(result["evidence"], ensure_ascii=False),
            supersedes
        ))
        rid = cur.lastrowid
        con.commit()
        con.close()
        return rid
