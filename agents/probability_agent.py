
import numpy as np

class ProbabilityAgent:
    """Empirical probability from historical next-day market changes."""
    def __init__(self,daily): self.daily=daily

    def forecast(self,market):
        g=self.daily[self.daily["market"].str.contains(market,case=False,regex=False)].sort_values("date")
        moves=g["rate"].diff().shift(-1).dropna().values
        if len(moves)==0:
            return {"p_up":.33,"p_flat":.34,"p_down":.33,"expected_change":0,"confidence":.15,"sample":0}
        p_up=float((moves>5).mean())
        p_down=float((moves<-5).mean())
        p_flat=1-p_up-p_down
        return {"p_up":p_up,"p_flat":p_flat,"p_down":p_down,
                "expected_change":float(np.mean(moves)),
                "confidence":min(.90,.25+len(moves)/40),
                "sample":len(moves)}
