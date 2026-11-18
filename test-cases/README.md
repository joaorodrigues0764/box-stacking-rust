# Solver validation

Run from the repository root with Python 3 and Cargo installed:

```bash
python3 test-cases/validate.py
```

The script builds the release executable and checks its actual standard output.
It uses only the Python standard library. The default random seed is `2026`.

This is the project's correctness suite. There are currently no Rust unit tests,
so `cargo test` alone does not validate the solver's behavior.

The independent quadratic oracle enumerates all six rotations and processes them
by base area. It does not use the Rust implementation's normalized bases,
width ordering, coordinate compression, or Fenwick tree.

For every case, the checker verifies the optimal height, the reported block
count, the availability of every block orientation, the sum of the heights, and
strictly decreasing base dimensions. It accepts different optimal towers.
The checker also tests itself against deliberately invalid outputs.

Coverage includes:

- Small worked examples, repeated dimensions, and signed 32-bit boundary values.
- All 285 multisets of one to three types with dimensions from 1 to 3.
- 2,000 random cases, including many ties and shared dimensions.
- 100 shuffled cases with permuted input dimensions.
- A tower of 60,000 cubes and 100,000 duplicate types.

Each solver invocation has a 10-second timeout. The large cases have known
optimal heights and do not run the quadratic oracle. On failure, the script
saves the input to `test-cases/failure.in` and exits with a nonzero status.

To use a different seed or an existing executable:

```bash
python3 test-cases/validate.py --seed 42 --random-cases 5000
python3 test-cases/validate.py --binary ./target/release/asa_project --skip-stress
```

These checks provide evidence of correctness. They do not measure performance;
see `benchmarks/README.md` for runtime and memory measurements.
