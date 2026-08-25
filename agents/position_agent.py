
class PositionAgent:
    """
    Market-only recommendation.
    IMPORTANT: inventory is deliberately absent.
    This agent answers: what should a market participant do given current evidence?
    """
    def decide(self, regime, p_up, p_down, confidence, expected_change):
        if confidence < 0.35:
            action = "WAIT"
        elif p_up >= 0.62 and expected_change > 0:
            action = "HOLD"
        elif p_down >= 0.62 and expected_change < 0:
            action = "SELL"
        elif p_up > p_down and expected_change > 0:
            action = "HOLD"
        elif p_down > p_up and expected_change < 0:
            action = "SELL"
        else:
            action = "WAIT"

        risk = "LOW"
        if confidence < 0.55:
            risk = "HIGH"
        elif confidence < 0.72:
            risk = "MEDIUM"

        return {
            "action": action,
            "risk": risk,
            "conviction": confidence
        }
