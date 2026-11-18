# Input generator

`gerador.cpp` generates distinct block types for the box-stacking solver.
Two types count as the same when their dimensions differ only by permutation.
The tool randomizes the dimension order of each generated type.

## Build

From the repository root, with a C++11 compiler or newer:

```bash
g++ -std=c++11 -O2 -Wall -Wextra tools/gerador.cpp -o gerador
```

The generated executable at the repository root is ignored by Git.

## Usage

```text
./gerador <num_blocks> <max_dimension> [seed]
```

- `num_blocks`: positive number of distinct block types to generate.
- `max_dimension`: positive upper bound for each dimension, inclusive.
- `seed`: optional nonnegative seed. Without it, the tool uses `random_device`.

Arguments must fit in a signed `int`. For a dimension bound `d`, there are
`d * (d + 1) * (d + 2) / 6` distinct types. Requests above this count are rejected
when `d <= 1,000,000`; larger bounds already offer more types than the supported
block-count range can request. Large requests can require substantial memory.

For repeatable inputs, provide a seed and use the same executable and C++
standard library implementation.

Generate 1,000 types with dimensions from 1 to 100:

```bash
./gerador 1000 100 2026 > teste_1000.in
cargo run --release < teste_1000.in
```

The output starts with the number of types, followed by one triple per line.
Files named `teste_*.in` at the repository root are ignored by Git.

This tool is optional. The Python correctness and benchmark suites generate
their own inputs and do not depend on it.
