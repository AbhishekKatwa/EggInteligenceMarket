
import numpy as np

class CrossMarketAgent:
    """Tests whether broad regional movement confirms or contradicts target market."""
    def __init__(self,daily): self.daily=daily

    def analyze(self,target):
        x=self.daily.sort_values("date").copy()
        latest=x.groupby("market").tail(2)
        if latest.empty:
            return {"signal":50,"confidence":.10,"breadth_up":.5,"evidence":["NO_CROSS_MARKET_DATA"]}
        changes=latest.groupby("market")["rate"].last()-latest.groupby("market")["rate"].first()
        changes=changes.dropna()
        if len(changes)==0:
            return {"signal":50,"confidence":.10,"breadth_up":.5,"evidence":["NO_BREADTH"]}
        up=float((changes>0).mean())
        signal=float(np.clip(100*up,0,100))
        return {"signal":signal,"confidence":min(.90,.30+len(changes)/100),
                "breadth_up":up,"evidence":[f"markets={len(changes)}",f"breadth_up={up:.2%}"]}
