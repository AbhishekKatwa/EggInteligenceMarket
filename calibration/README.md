# Phase 17.7 — Probability Calibration

The adaptive model produces a directional probability proxy. This phase calibrates that probability online using only prior observations.

Outputs:
- calibrated predictions
- raw vs calibrated Brier score
- reliability table
- regime calibration

The final model should still be evaluated on an untouched holdout before live use.
