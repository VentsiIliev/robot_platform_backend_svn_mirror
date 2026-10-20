Descriptor-ranking experiment
=============================

This standalone probe reads the existing immutable JSON test library. It creates
a separate NPZ cache and does not change robot-system code, JSON records, or
existing SQLite indexes. Keep the cache outside Git.

Run a quick query on the saved 100,000-item library:

```bash
.venv/bin/python scripts/workpiece_descriptor_probe.py --root "$HOME/Downloads/workpiece-benchmark-100000" --cache /tmp/workpiece-descriptors-100000.npz --query-indices 0 --variants rotated --top-k 20 --query-only
```

The first run builds the cache once from existing JSON. Later runs load it.
For a durable cache across reboots, choose an existing directory outside `/tmp`,
for example `--cache "$HOME/Downloads/workpiece-descriptors-100000.npz"`.
Treat the library as immutable: cache loading checks its root and descriptor
version but does not scan for edits. Use a new cache file after changing JSON.

Validate rectangle, circle, and T-shape queries against a slow full scan:

```bash
.venv/bin/python scripts/workpiece_descriptor_probe.py --root "$HOME/Downloads/workpiece-benchmark-100000" --cache /tmp/workpiece-descriptors-100000.npz --query-indices 0 2 8 --variants rotated
```

Without `--query-only`, a full reference scan follows the fast queries. It can
take minutes and is validation work, not part of the ranked query latency.
Defaults validate the first nine library records under rotation, reflection,
and 5% scaling, with both top-20 and top-50 caps. `--query-only` explicitly marks
reference-dependent correctness metrics as null/unverified.

How the experiment works
------------------------

For each contour, sample 256 points at equal arc-length intervals, calculate
their distances from the area centroid, and retain 24 normalized Fourier
magnitudes. These features approximately ignore rotation, reflection, starting
vertex, and scale. Sampling and discarded Fourier phase mean distinct contours
can share similar descriptors; ranking is not proof of a match.

Keep the full matcher's area-ratio eligibility gate (0.80), rank eligible records
using a combination of log area difference and descriptor distance, and run
the existing accurate geometric scorer only on the selected top K. The ranking
weight is experimental. Descriptors are loaded into memory once; each query
uses vectorized NumPy operations instead of loading thousands of JSON records.

Each `query_seconds` measurement includes descriptor extraction, area filtering,
ranking, loading selected JSON files, and accurate scoring. Cache construction,
cache loading, Python imports, camera capture, alignment, and robot workflow
execution are excluded. Preparation/cache load times are reported separately;
`startup_seconds` starts after Python imports. Filesystem caching can affect times.

Correctness metrics distinguish retaining the deterministic full-scan best ID
(`same_best`) from retaining its exact score (`same_best_score`). The script
exits nonzero if a validated best ID changes. It reports accepted matches outside
the cap, which are expected with top-K ranking; it does not claim to return every
accepted match. Inspect the score gap when geometrically near-identical records
produce different IDs. Synthetic tests do not establish accuracy on real captures.

Observed validation results
---------------------------

On the 1,000-record synthetic library, all 27 transformed queries retained the
exact full-scan best ID and score with both caps. Top-20 queries took 0.094–0.318
seconds; top-50 queries took 0.124–0.629 seconds.

On the saved 100,000-record library, three rotated queries also retained the exact
full-scan best ID and score with both caps:

| Query | Top 20 | Top 50 | Full reference scan |
|---|---:|---:|---:|
| Rectangle | 0.150 s | 0.347 s | 76.75 s |
| Circle | 0.138 s | 0.280 s | 114.52 s |
| T-shape | 0.279 s | 0.737 s | 94.44 s |

The descriptor cache took 33.67 seconds to build once. A later query-only process
loaded it in 0.072 seconds and executed its top-20 query in 0.184 seconds; total
fresh CLI process time was 3.02 seconds, including Python imports/startup. A
long-running application would load the cache once. Real camera data, measurement
noise, no-match cases, and other libraries still need validation before integration.
