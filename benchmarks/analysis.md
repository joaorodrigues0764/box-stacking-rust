# Interpretation of the local results

The experiment records 150 measured executions: five input families, six sizes,
and five repetitions. Each dataset also has one unrecorded warm-up.
The full table and raw samples are in `results/summary.md` and
`results/samples.csv`. Compiler and machine details are in `results/environment.json`.

## Runtime

At 320,000 input types, median wall times range from 30.323 ms for duplicate
cubes to 287.341 ms for wide coordinates. The random family takes 222.890 ms.

The wide family retains many distinct lengths, so it exercises larger
compression and Fenwick arrays. Doubling its size from 160,000 to 320,000
multiplies median time by 2.25; n log2(n) grows by about 2.12.
Its normalized time is about 46-51 ns for sizes from 80,000 to 320,000.
This is consistent with the theoretical analysis, without proving it.

Duplicate cubes are much faster because compression produces one length and
all records compare equal. The other bounded-coordinate families eventually
repeat many dimensions. Do not claim that every family must exhibit the same
n log(n) curve: the worst-case upper bound allows easier inputs.

## Memory

For wide coordinates, median peak RSS grows from 27.42 MiB at 160,000 types to
53.31 MiB at 320,000 types. This is consistent with linear storage.
The random and duplicate families use 36.87 MiB and 33.23 MiB at 320,000 types.
Coordinate cardinality and reconstruction length affect the constant factors.

## Limitations and report use

All measurements include process launch, input reading, reconstruction, and
output formatting to `/dev/null`. Input generation and compilation are excluded.
The C launcher measures each solver with `wait4`, without inheriting the Python
driver's large pre-exec memory footprint. A preliminary Python-based measurement
was discarded after detecting that memory bias; the saved samples use the C launcher.

The machine was not isolated from other workloads and no CPU affinity was set.
Small timings and ranges show scheduling and frequency variation. Use medians,
identify the machine and compiler, and avoid interpreting small differences as
algorithm improvements. Local results do not establish Mooshak time or memory limits.

For a two-page report, use the wide-coordinate family for the principal scaling
plot and a compact comparison at the largest size for the other families.
Keep the correctness argument and theoretical bounds separate from this evidence.
