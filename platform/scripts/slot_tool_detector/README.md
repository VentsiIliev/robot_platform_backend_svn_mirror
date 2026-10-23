Slot occupancy detector
=======================

The existing `data/<slot>/{empty,occupied}` full-frame images can be reused;
no recapture is needed to train the upgraded detector. Polygons must match the
image resolution and camera position.

Train and run the upgraded model with the platform virtual environment:

```bash
../../.venv/bin/python calibrate_slots.py --config slots.json --data data --out slots_robust.json --model forest --refit-all
../../.venv/bin/python slot_widget.py --config slots_robust.json --camera 0
```

`slots_robust.json` is already trained from the supplied dataset. Its matching
`slots_robust_assets_*` directory contains per-slot forests and empty references.
Keep the referenced directory with the JSON. References load automatically; do
not press “Set empty reference” during ordinary startup. Only replace a reference
when the corresponding slot is known to be empty. Camera frames must be 640×480
for the supplied configuration. The capture app remains available for adding
examples, using `--config slots.json --data data`.

The forest uses 20 features: the original edge density, changed-pixel fraction
and contrast ratio, plus mean/90th-percentile reference differences, largest
connected changed area, gradient statistics, intensity spread, entropy, reference
correlation and nine spatial difference cells. The
[OpenCV RTrees API](https://docs.opencv.org/3.4.20/d0/d65/classcv_1_1ml_1_1RTrees.html)
provides the model and per-class tree votes. The displayed score is the fraction
of trees voting occupied; it is not a calibrated probability. Forest thresholds
are fixed at 0.1/0.9 by default (`--margin 0.4`). In-sample tree votes must not
be used to tighten these thresholds toward 0/1; they overstate certainty.
Scores between the saved thresholds produce UNKNOWN, followed by temporal voting.
Feature extraction runs locally around each slot. No extra ML dependency is
required beyond the existing OpenCV/NumPy environment.

Legacy configurations retain their original three-feature classifier. Calibration
defaults to logistic regression with those features; `--model forest` selects
schema 2. Use `--features 1` or `--features 2` to explicitly compare either model
with either schema.

Forest training generates 12 mild lighting/position variants per original frame:
gain 0.65–1.35, offset ±25, a spatial brightness ramp and translation up to two
pixels. These variants are generated after splitting originals, so held-out
images and their variants never enter the validation model's training set.
`--augment 0` disables generation; logistic training defaults to zero variants.

Validation uses the last 25% of unique images in each class, in filename order.
Only training empty images contribute to the validation model's median reference.
Exact within-class duplicates are removed and conflicting labels are rejected.
Results are saved in `<output>.report.json`, with UNKNOWN and wrong predictions
reported separately. Forest thresholds are fixed before validation. Logistic
thresholds retain the conservative training-range behavior of the baseline.

Without `--refit-all`, saved models retain this split. With `--refit-all`, the
report describes validation **before refitting**, then the saved model and its
reference are retrained using every available original. The saved model's
performance on those images is consequently a training regression check, not
held-out accuracy. `--exclude-image path/to/frame.png` (repeatable) excludes a
specific frame from both stages, including reference construction.

The current model includes the four newly labeled captures from the live failure.
The original model's threshold of 0.98 rejected a new occupied frame scoring
0.935, and changed backgrounds also produced UNKNOWN states. Augmentation,
fixed forest thresholds, and refitting with the new labeled examples address
that case. Capture bursts can be highly correlated; new-session examples are
still needed to measure generalization. UNKNOWN remains appropriate for
unrecognized backgrounds or partial occlusions.

The viewer title shows the loaded configuration filename. Restart it after
retraining to load the new model files. Empty references load automatically;
setting one manually is not a required startup step.

Verification:

```bash
../../.venv/bin/python -B -m unittest test_slot_detector -v
../../.venv/bin/python -B ttest_synthetic.py
```

Changing a trained polygon or preprocessing settings requires retraining. The
loader checks these against the saved reference and rejects mismatches.

Inspection regions that exclude the floor
----------------------------------------

Use the new `slots_inspection.json` configuration to inspect only the central
hub/backplate area, rather than the entire opening:

```bash
../../.venv/bin/python slot_widget.py --config slots_inspection.json --camera 0
```

Dashed polygons show full slot outlines. Solid polygons show the actual
inspection regions; only pixels inside these contribute to the model. The
starting rectangles cover the central 70% of slot width and the vertical range
30%–85% down each slot, excluding the exposed floor above the fixed backplate.
The original `slots_robust.json` remains available.

Each slot has an optional `inspection_polygon` and `local_preprocessing` flag.
With local preprocessing enabled, outside pixels are excluded before blur and
CLAHE, so even contrast normalization cannot carry floor changes into the
inspection region. The inspection region is intersected with the full slot mask.

The viewer's handles edit the solid inspection polygon. After adjusting it,
click Save config, close the viewer, and retrain before reopening:

```bash
../../.venv/bin/python calibrate_slots.py --config slots_inspection.json --data data --out slots_inspection.json --model forest --refit-all
```

`slots_inspection_base.json` preserves the initial untrained inspection geometry.
Calibration can retrain edited geometry without loading obsolete model/reference
artifacts. Runtime loading rejects artifacts trained for a different region.

Checks on the current model: all 127 labeled training examples classify
correctly after refitting. Pre-refit validation reports 32 correct, two UNKNOWN,
and no wrong predictions over 34 examples. Changing every pixel outside a
region leaves its features identical. These checks establish background
isolation and regression behavior; they do not prove arbitrary foreign-object
rejection. Objects that enter the inspected area can still affect the result.

Editing a region pauses inference and keeps every slot UNKNOWN until retraining;
replacing an empty reference cannot reactivate a model trained for the old region.
The viewer keeps a save/retrain reminder visible. If a saved region differs from
the trained artifacts on startup, a dialog gives the retraining command instead
of an uncaught traceback.
