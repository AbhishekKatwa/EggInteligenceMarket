
class RiskAgent:
    """Risk assessment only. Never sizes inventory."""
    def assess(self, confidence, p_up, p_down, source_conflict=False):
        if source_conflict:
            return {"risk": "HIGH", "risk_flags": ["SOURCE_CONFLICT"]}
        if confidence < .45:
            return {"risk": "HIGH", "risk_flags": ["LOW_CONFIDENCE"]}
        if abs(p_up-p_down) < .12:
            return {"risk": "MEDIUM", "risk_flags": ["DIRECTION_UNCERTAIN"]}
        return {"risk": "LOW", "risk_flags": []}
