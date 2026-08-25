
class LearningAgent:
    """Scores prior recommendations against realized outcomes."""
    def score(self, recommendations, outcomes):
        if not outcomes:
            return {"n":0,"avg_pnl":None,"win_rate":None}
        pnl=[x.get("pnl_per_egg",0) for x in outcomes]
        return {"n":len(pnl),"avg_pnl":sum(pnl)/len(pnl),
                "win_rate":sum(1 for x in pnl if x>0)/len(pnl)}
