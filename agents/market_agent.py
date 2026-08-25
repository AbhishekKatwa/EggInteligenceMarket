
import re, numpy as np, pandas as pd

class MarketAgent:
    """Numerical market state from historical structured observations."""

    def __init__(self, daily_market):
        self.daily = daily_market.copy()

    def state(self, market):
        g = self.daily[self.daily["market"].str.contains(market, case=False, regex=False)].sort_values("date")
        if g.empty:
            return {"market": market, "signal": 50, "confidence": .15, "evidence": ["NO_HISTORY"]}
        rates = g["rate"].astype(float)
        cur = rates.iloc[-1]
        def delta(n):
            return cur-rates.iloc[-n-1] if len(rates)>n else 0
        d1=delta(1); d3=delta(3); d7=delta(7)
        recent = g["change"].dropna().tail(14)
        vol=float(recent.std()) if len(recent)>1 else 10
        # Momentum signal 0-100
        signal=float(np.clip(50 + 2.5*d1 + 1.2*d3 + .5*d7,0,100))
        conf=min(.95,.30+.04*min(len(g),15))
        return {
            "market":market,"current_rate":float(cur),"d1":float(d1),
            "d3":float(d3),"d7":float(d7),"volatility":vol,
            "signal":signal,"confidence":conf,
            "evidence":[f"d1={d1:.1f}",f"d3={d3:.1f}",f"d7={d7:.1f}",f"vol={vol:.1f}"]
        }
