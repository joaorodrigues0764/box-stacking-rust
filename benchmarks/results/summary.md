# Local benchmark results

Times include process launch, input reading, computation, reconstruction,
and output formatting. Output is written to `/dev/null`.
Input generation, compilation, and launcher startup are excluded.
Each dataset has one unrecorded warm-up followed by repeated measurements.
Peak RSS is reported by Linux for each solver child; Python driver memory
is not included. Small timings are sensitive to launch and scheduling noise.

| Family | Types | Median wall (ms) | Wall min-max (ms) | Median CPU (ms) | Median peak RSS (MiB) | Wall / (n log2 n) (ns) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| random | 10000 | 10.752 | 9.975-10.867 | 10.382 | 3.63 | 80.92 |
| random | 20000 | 17.293 | 16.774-21.294 | 16.860 | 4.69 | 60.52 |
| random | 40000 | 36.198 | 31.713-38.270 | 35.903 | 6.86 | 59.19 |
| random | 80000 | 62.616 | 55.041-69.661 | 62.087 | 11.16 | 48.05 |
| random | 160000 | 113.453 | 109.777-126.027 | 111.383 | 19.71 | 41.02 |
| random | 320000 | 222.890 | 210.136-229.813 | 219.378 | 36.87 | 38.09 |
| shared | 10000 | 12.818 | 8.302-13.259 | 12.370 | 3.66 | 96.46 |
| shared | 20000 | 19.741 | 18.235-21.356 | 19.402 | 4.63 | 69.08 |
| shared | 40000 | 34.256 | 32.319-38.206 | 32.713 | 6.93 | 56.02 |
| shared | 80000 | 49.619 | 47.862-57.869 | 49.081 | 11.01 | 38.08 |
| shared | 160000 | 90.571 | 87.688-96.457 | 89.915 | 19.58 | 32.74 |
| shared | 320000 | 171.041 | 161.411-178.704 | 169.298 | 36.63 | 29.23 |
| wide | 10000 | 9.188 | 7.604-9.653 | 8.812 | 3.75 | 69.14 |
| wide | 20000 | 15.661 | 14.734-18.599 | 15.329 | 5.38 | 54.81 |
| wide | 40000 | 31.953 | 29.227-36.466 | 31.320 | 8.61 | 52.25 |
| wide | 80000 | 66.761 | 66.055-72.972 | 66.283 | 14.82 | 51.24 |
| wide | 160000 | 127.842 | 122.860-136.813 | 127.016 | 27.42 | 46.22 |
| wide | 320000 | 287.341 | 264.696-310.442 | 283.597 | 53.31 | 49.10 |
| duplicates | 10000 | 3.202 | 3.069-3.577 | 3.017 | 3.27 | 24.10 |
| duplicates | 20000 | 4.788 | 3.899-5.921 | 4.502 | 4.20 | 16.75 |
| duplicates | 40000 | 6.883 | 6.726-9.321 | 6.589 | 6.23 | 11.26 |
| duplicates | 80000 | 12.161 | 7.727-14.769 | 11.758 | 10.04 | 9.33 |
| duplicates | 160000 | 20.280 | 13.582-24.064 | 19.915 | 17.86 | 7.33 |
| duplicates | 320000 | 30.323 | 24.884-34.795 | 29.842 | 33.23 | 5.18 |
| cubes | 10000 | 6.005 | 5.675-9.182 | 5.719 | 3.79 | 45.19 |
| cubes | 20000 | 11.413 | 9.085-12.024 | 11.140 | 5.15 | 39.94 |
| cubes | 40000 | 22.124 | 16.814-23.559 | 21.679 | 8.12 | 36.18 |
| cubes | 80000 | 48.379 | 38.633-70.669 | 47.763 | 13.09 | 37.13 |
| cubes | 160000 | 75.404 | 74.195-79.918 | 74.684 | 21.66 | 27.26 |
| cubes | 320000 | 131.036 | 129.157-133.066 | 128.647 | 38.96 | 22.39 |

These observations do not prove an asymptotic bound or establish
the time and memory available on Mooshak.
