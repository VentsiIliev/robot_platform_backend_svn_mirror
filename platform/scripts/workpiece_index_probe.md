Standalone workpiece-index benchmark
==================================

Create a reusable library once (choose a directory that does not exist):

```bash
.venv/bin/python scripts/workpiece_index_probe.py --generated-count 10000 --save-library "$HOME/Downloads/workpiece-benchmark-10000" --prepare-only
```

Benchmark it repeatedly without generating files or rebuilding the index:

```bash
.venv/bin/python scripts/workpiece_index_probe.py --root "$HOME/Downloads/workpiece-benchmark-10000" --queries 9
```

Use a durable output directory to retain data across reboots. `/tmp` can be
cleaned by the operating system. Keep generated datasets outside Git.

The output directory contains sharded JSON records, `probe-library.json` completion
metadata, and `index-geometry-v2.db`. Older area-only `index.db` files are retained;
the richer index is built once from existing JSON without regenerating the library.
Treat completed datasets as immutable and keep them at
their original path: the index contains absolute paths. Use a new directory to
change dataset size or regenerate it. Interrupted preparation leaves
`.probe-incomplete` and is rejected on reuse. Ordinary workpiece libraries supplied
through `--root` are read only; their experimental index is temporary.

The probe reuses the dry-run generator's configuration, dimension selection, and
shape creation functions without changing robot-system code. It streams records
instead of building the generator's large in-memory manifest, and disables previews.
Progress goes to stderr; the final JSON report goes to stdout.

Each query uses one saved contour, transformed by rotation, reflection, and 5%
scaling. The query count is capped at the available records. The SQLite
shortlist is compared with a full scan using the current geometric scorer. No robot,
camera, process workflow, or production repository is started.

The default `--filter geometry` combines area with minimum-area rectangle sides,
perimeter, convex-hull solidity, and structural vertex count. Sides must have a
minimum/maximum ratio of at least 0.75, perimeter at least 0.80, and vertex count
at least 0.70; solidity may differ by at most 0.12. These are experimental gates,
not guaranteed mathematical bounds on every shape the full matcher accepts.
The probe returns a nonzero status if any accepted match is excluded or the best
match changes. It reports area-only and stronger candidate counts, SQL query time,
matching time, and speedup. `--filter area` selects the original area-only baseline.

For a shorter first check on the saved 100,000-item library:

```bash
.venv/bin/python scripts/workpiece_index_probe.py --root "$HOME/Downloads/workpiece-benchmark-100000" --queries 1 --variants rotated
```

Use `--index-path /tmp/workpiece-geometry-v2.db` to keep the new index separate
from the library. An index is rejected if its stored paths differ from the current
library. JSON edits are not detected: benchmark libraries must remain immutable.

The 10,000-item sample allocated about 67.5 MiB including the index, excluding
directory/inode overhead. A million files would need roughly 6.6 GiB or more;
check free disk space before starting. Substitute `1000000` in the preparation
command on a sufficiently large disk, then start benchmarking with `--queries 1`.

These synthetic data use nine shape families with varying dimensions, rather than
a million unrelated real-world geometries. Timings include JSON reads and scoring,
but exclude preparation, initial directory discovery, and the complete production
workflow. Full scans precede shortlist scans, so filesystem caching can influence
the timings. This is a correctness and scaling experiment, not a production latency
guarantee.

Observed validation results
---------------------------

- 1,000 records, nine query shapes and three transformations (27 cases): zero
  excluded accepted matches and zero best-match changes. Full scans totalled
  24.20 seconds; geometry-filtered scans including SQL queries totalled 11.54 seconds.
- Saved 100,000-record library, first rectangle rotated 37 degrees: area-only
  shortlist 18,974, geometry shortlist 3,325. Full scan 99.34 seconds versus
  28.78 seconds for geometry lookup plus scoring (3.45x). All 692 accepted matches
  were retained and the best match agreed. Index construction took 29.90 seconds.

An initial 0.80 dimension-ratio gate excluded an ellipse accepted by the matcher
for hexagon queries. Widening the dimension gate to 0.75 fixed those observed
exclusions. This illustrates why every additional gate needs recall checks;
the measurements above do not establish correctness for arbitrary real captures.
