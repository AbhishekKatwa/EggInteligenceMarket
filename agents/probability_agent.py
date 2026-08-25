
import numpy as np

class ProbabilityAgent:
    """
    Empirical forecast from historical next-observation moves.
    No inventory, no position sizing.
    """

    def __init__(self, daily):
        self.daily = daily

    def forecast(self, market, as_of=None):
        g = self.daily[
            self.daily["market"].str.contains(market, case=False, regex=False)
        ].sort_values("date")

        if as_of is not None:
            g = g[g["date"] <= as_of]

        moves = g["rate"].diff().shift(-1).dropna().values

        if len(moves) == 0:
            return {
                "p_up": 1/3, "p_flat": 1/3, "p_down": 1/3,
                "expected_change": 0.0,
                "confidence": 0.15,
                "sample": 0
            }

        up = moves > 5
        down = moves < -5
        flat = ~(up | down)

        p_up = float(up.mean())
        p_down = float(down.mean())
        p_flat = float(flat.mean())

        # Shrink tiny samples toward neutral.
        n = len(moves)
        prior = 10
        p_up = (p_up*n + 1/3*prior)/(n+prior)
        p_down = (p_down*n + 1/3*prior)/(n+prior)
        p_flat = (p_flat*n + 1/3*prior)/(n+prior)

        return {
            "p_up": p_up,
            "p_flat": p_flat,
            "p_down": p_down,
            "expected_change": float(np.mean(moves)),
            "confidence": min(.92, .25 + n/50),
            "sample": n
        }
