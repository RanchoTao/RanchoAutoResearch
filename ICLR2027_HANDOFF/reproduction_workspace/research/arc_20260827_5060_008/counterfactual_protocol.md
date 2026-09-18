# Counterfactual protocol

1. Extract outcome-blind block/noise directions at the frozen residual-stream
   site for all 103 cells.
2. Run Stage A1 and freeze its artifacts before joining corrected outcomes.
3. If technical and direction-distinct gates pass, calibrate alpha on seed 11
   using KL, NLL, hidden norm, output-logit norm, and boundary alignment only.
4. Freeze each cell's selected alpha pair and match status.
5. Reveal canonical top-1 damage on held-out seeds 23 and 37.
6. Apply the confirmatory balance calipers without modification.
7. Report every cell, failed calibration, excluded cell, run, checkpoint, and
   layer; summarize uncertainty at run level.

The existing Gaussian noise directions also serve as the fixed random-direction
control. The calibration alpha grid supplies the outcome-blind
direction-preserving magnitude diagnostic. No additional random search is run.
