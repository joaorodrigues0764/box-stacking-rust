# Performance measurements

Run after the correctness suite, on Linux with Python 3, Cargo, and a C compiler (`cc`):

```bash
python3 benchmarks/measure.py
```

No Python packages are required. The script builds the optimized solver,
creates one input at a time in a temporary directory, warms up the executable,
and takes five samples per dataset. The default sizes double from 10,000 to
320,000 input types. Input files are removed at the end.

Five input families exercise different behavior:

- `random`: independent dimensions from 1 to 20,000, including repeated coordinates.
- `shared`: all types have one dimension equal to 500, producing many ties.
- `wide`: one dimension is 1, while the others vary up to one billion. This
  exercises compression with many distinct coordinates while limiting tower height.
- `duplicates`: identical cubes of side 7; the optimum is always 7.
- `cubes`: cubes with sides cycling from 1 to 60,000. The optimum is the sum
  from 1 to min(n, 60,000). Cycling keeps the height within signed 32-bit range.

All families satisfy the statement's height bound. For `random` and `shared`,
a tower has at most 20,000 blocks, each at most 20,000 high. For `wide`, at most
one block with base width 1 can occur; all other blocks have height 1. Thus its
height is at most one billion plus n. Input order and seed are reproducible;
execution times depend on the machine and system load.

The output directory contains:

- `samples.csv`: wall time, CPU time, and peak resident memory for every run.
- `environment.json`: compiler, machine, seed, sizes, timestamps, and source,
  executable, and input hashes.
- `summary.md`: medians, wall-time ranges, memory, and normalized wall time.

Measurements include input reading and output formatting, with standard output
redirected to `/dev/null`. They exclude compilation and input generation.
A small C launcher uses `wait4` to collect statistics for each solver process.
It avoids inheriting the Python driver's memory footprint in the measured peak.
Peak RSS uses Linux KiB units. Launcher compilation and startup are excluded;
solver process launch and waiting overhead are included. Each child has an
alarm timeout, rounded up to whole seconds.

To write a smaller experiment separately:

```bash
python3 benchmarks/measure.py --sizes 10000 20000 --runs 3 --output /tmp/asa-benchmark
```

These are local measurements, not Mooshak limits or a proof of complexity.
The correctness suite remains in `test-cases/validate.py`.
