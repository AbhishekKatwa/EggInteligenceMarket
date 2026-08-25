
class PositionAgent:
    def decide(self,regime,forecast_conf,inventory):
        base={
            "GENUINE_BULL":.20,"GENUINE_BEAR":.85,"PANIC":.40,
            "EUPHORIA":.70,"CAPITULATION":.20,"NORMAL":.50,"CONFLICTED":.50
        }.get(regime,.50)
        # Low forecast confidence pulls toward neutral 50%.
        sell=.50+(base-.50)*min(1,forecast_conf/.70)
        sell=max(.10,min(.90,sell))
        if inventory<=0: sell=0
        action="SELL" if sell>=.70 else ("HOLD" if sell<=.30 else "PARTIAL_SELL")
        return {"sell_percent":sell,"hold_percent":1-sell,
                "sell_quantity":round(inventory*sell),
                "hold_quantity":inventory-round(inventory*sell),
                "action":action}
