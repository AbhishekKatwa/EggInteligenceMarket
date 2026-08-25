
import numpy as np

POS = ["strong","better","increase","plus","rise","recovery","support","buying",
       "shortage","तेजी","बढ़","सुधार","सपोर्ट","खरीद"]
NEG = ["weak","pressure","panic","down","fall","decline","slow","low demand",
       "sell","selling pressure","fear","कमजोर","दबाव","गिरावट","घबर","कम डिमांड"]

class CrowdAgent:
    """Language-derived crowd psychology. Returns signal, not a price prediction."""

    def analyze(self, messages):
        pos=sum(str(x).lower().count(t) for x in messages for t in POS)
        neg=sum(str(x).lower().count(t) for x in messages for t in NEG)
        total=pos+neg
        sentiment=float(np.clip(50+50*np.tanh((pos-neg)/max(3,total/2)),0,100))
        fear=float(np.clip(50+50*np.tanh((neg-pos)/max(3,total/2)),0,100))
        evidence=[f"positive_hits={pos}",f"negative_hits={neg}"]
        if fear>=80: evidence.append("EXTREME_FEAR")
        if sentiment>=80: evidence.append("EXTREME_EUPHORIA")
        return {"sentiment":sentiment,"fear":fear,
                "signal":sentiment,"confidence":min(.90,.30+total/100),
                "evidence":evidence}
