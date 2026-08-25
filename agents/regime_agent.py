
class RegimeAgent:
    def classify(self,crowd,sd,market,cross):
        s=crowd.get("sentiment",50)
        d=sd.get("demand",50)
        t=sd.get("supply_tightness",50)
        m=market.get("signal",50)
        b=cross.get("signal",50)

        if s>=75 and d>=65 and t>=65 and m>=50 and b>=55:
            return "GENUINE_BULL",.90
        if s<=25 and d<=35 and t<=35 and m<=45 and b<=45:
            return "GENUINE_BEAR",.90
        if s<=25 and t>=45 and d>=40:
            return "PANIC",.78
        if s>=75 and (t<55 or d<55):
            return "EUPHORIA",.78
        if s<=20 and abs(m-50)<12 and t>=50:
            return "CAPITULATION",.70
        if abs(s-50)<15 and abs(d-50)<15 and abs(t-50)<15:
            return "NORMAL",.60
        return "CONFLICTED",.65
