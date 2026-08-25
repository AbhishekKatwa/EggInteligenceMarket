
class RiskAgent:
    def apply(self,decision,confidence,conflict=False):
        if conflict or confidence<.45:
            # Conservative cap
            decision["sell_percent"]=min(decision["sell_percent"],.60)
            decision["hold_percent"]=1-decision["sell_percent"]
            decision["action"]="WAIT" if confidence<.35 else decision["action"]
        decision["risk_cap_applied"]=bool(conflict or confidence<.45)
        return decision
