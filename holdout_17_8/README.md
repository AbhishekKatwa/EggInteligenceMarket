# Phase 17.8 — Final Untouched Holdout

Chronological 80/20 split.

The final 20% of historical dates are held out completely.
Signal weights are learned only from the first 80%.
The learned model is frozen and evaluated on the final 20%.

This is the first clean test of whether the market brain generalizes beyond the data used for model selection.
