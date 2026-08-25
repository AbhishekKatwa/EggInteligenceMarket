
import numpy as np

DEMAND_POS=["demand good","demand strong","strong demand","good demand","buying strong",
            "lifting good","loading good","डिमांड अच्छी","मांग अच्छी","खरीद अच्छी"]
DEMAND_NEG=["demand weak","weak demand","low demand","limited demand","buyers limited",
            "lifting weak","lifting slow","buying weak","डिमांड कमजोर","मांग कमजोर","खरीदार कम"]
SUPPLY_HIGH=["supply high","more supply","heavy supply","supply ज्यादा","supply अधिक",
             "material available","availability good"]
SUPPLY_TIGHT=["supply tight","shortage","short supply","less supply","supply low",
              "material shortage","कम सप्लाई","सप्लाई कम"]

class SupplyDemandAgent:
    def analyze(self,messages):
        blob=" ".join(map(str,messages)).lower()
        def hits(words): return sum(blob.count(x) for x in words)
        dp,dn,sh,st=hits(DEMAND_POS),hits(DEMAND_NEG),hits(SUPPLY_HIGH),hits(SUPPLY_TIGHT)
        demand=float(np.clip(50+50*np.tanh((dp-dn)/max(2,(dp+dn)/2)),0,100))
        tight=float(np.clip(50+50*np.tanh((st-sh)/max(2,(st+sh)/2)),0,100))
        return {"demand":demand,"supply_tightness":tight,
                "signal":(demand+tight)/2,
                "confidence":min(.90,.30+(dp+dn+sh+st)/100),
                "evidence":[f"demand={demand:.1f}",f"supply_tightness={tight:.1f}",
                             f"hits={dp}/{dn}/{sh}/{st}"]}
