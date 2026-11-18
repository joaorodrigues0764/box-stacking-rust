# Box Stacking in Rust

Find the tallest possible tower of rectangular blocks and reconstruct its
arrangement from base to top. The solver uses dynamic programming with a Fenwick
tree, taking **O(n log n) time** and **O(n) memory** for `n` block types.

## Problem

Each block type has three dimensions and is available in unlimited quantities.
Blocks may be rotated so that any dimension becomes the height. A block can sit
on another only when **both of its base dimensions are strictly smaller** than
those of the block below it.

The program returns the maximum total height and one tower that achieves it.
Multiple optimal arrangements may exist.

## Build and run

Install a Rust toolchain with support for the 2024 edition, including Cargo.
The solver has no external dependencies.

```bash
git clone https://github.com/joaorodrigues0764/box-stacking-rust.git
cd box-stacking-rust
cargo build --release
```

Run the solver with an input file:

```bash
./target/release/asa_project < input.txt
```

The Cargo package and executable are currently named `asa_project`.

### Input

The first integer is the number of block types, `n`. Each of the next `n` lines
contains three positive dimensions. Dimensions must fit in a signed 32-bit
integer. The solver assumes valid input; it does not provide validation messages
for malformed or incomplete data.

```text
1
5 10 20
```

### Output

The first line contains the maximum height and the number of blocks in the
tower. Each following line contains the width, length, and height of one block,
ordered from base to top.

```text
25 2
10 20 5
5 10 20
```

Here, two copies of the same block type are used in different orientations.
Total heights are accumulated using signed 64-bit integers.

## Algorithm

1. Generate three orientations per block type, choosing each dimension as the
   height. Normalize each base so that its width is no greater than its length.
2. Sort orientations by increasing width, breaking ties by decreasing length.
3. Compress the distinct base lengths into consecutive ranks.
4. For each orientation, query a Fenwick tree for the tallest tower whose base
   length is strictly smaller, then add the current block underneath it.
5. Store the selected predecessor for each orientation and follow those links
   to reconstruct the best tower.

The descending length order within equal widths prevents blocks of equal width
from being stacked: previously processed blocks of that width cannot appear in
a query for a strictly smaller length. Together with the strict length query,
this enforces both stacking constraints.

There are `3n` orientations. Sorting, coordinate lookup, and Fenwick operations
take O(n log n) time overall; the orientation, tree, and reconstruction arrays
use O(n) memory.

## Validation

With Python 3 and Cargo installed, run:

```bash
python3 test-cases/validate.py
```

The script builds the release executable, compares its results with an
independent quadratic solver, and validates every reconstructed tower. Its
default suite covers 2,394 cases, including exhaustive small inputs, random
inputs, dimension permutations, and large stress cases. It uses only the Python
standard library.

This Python suite is the correctness check; there are currently no Rust unit
tests for `cargo test` to execute. See [validation details](test-cases/README.md)
for options and failure diagnostics.

## Input generator

An optional C++ tool generates distinct block types with randomized dimension
ordering. See [the generator instructions](tools/README.md) for compilation,
arguments, and examples. It is not required by the solver or validation suite.

## Benchmarks

The benchmark suite measures runtime and peak resident memory across five input
families. It requires Linux, Python 3, Cargo, and a C compiler.

- [Run the benchmarks](benchmarks/README.md)
- [Recorded results](benchmarks/results/summary.md)
- [Analysis and measurement limitations](benchmarks/analysis.md)

Recorded timings are specific to the machine and source snapshot described in
`benchmarks/results/environment.json`; they are not performance guarantees.

## Repository layout

```text
src/main.rs       Solver and tower reconstruction
test-cases/       Independent correctness checks
tools/            Optional C++ input generator
benchmarks/       Measurement scripts, results, and analysis
```
