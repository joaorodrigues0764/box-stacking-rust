#!/usr/bin/env python3
"""Measure release solver time and peak RSS on reproducible Linux inputs."""

import argparse
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import random
import statistics
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
FAMILIES = ('random', 'shared', 'wide', 'duplicates', 'cubes')


def write_input(path, family, size, seed):
    rng = random.Random(seed + size)
    with path.open('w') as stream:
        stream.write(f'{size}\n')
        for index in range(size):
            if family == 'random':
                block = [rng.randint(1, 20000) for _ in range(3)]
            elif family == 'shared':
                block = [500, rng.randint(1, 20000), rng.randint(1, 20000)]
            elif family == 'wide':
                block = [1, rng.randint(2, 1000000000), rng.randint(2, 1000000000)]
            elif family == 'duplicates':
                block = [7, 7, 7]
            else:
                side = index % 60000 + 1
                block = [side, side, side]
            stream.write(' '.join(map(str, block)) + '\n')


def command_output(arguments):
    return subprocess.check_output(arguments, cwd=ROOT, text=True).strip()


def write_summary(destination, samples):
    lines = [
        '# Local benchmark results', '',
        'Times include process launch, input reading, computation, reconstruction,',
        'and output formatting. Output is written to `/dev/null`.',
        'Input generation, compilation, and launcher startup are excluded.',
        'Each dataset has one unrecorded warm-up followed by repeated measurements.',
        'Peak RSS is reported by Linux for each solver child; Python driver memory',
        'is not included. Small timings are sensitive to launch and scheduling noise.', '',
        '| Family | Types | Median wall (ms) | Wall min-max (ms) | Median CPU (ms) | Median peak RSS (MiB) | Wall / (n log2 n) (ns) |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for family in FAMILIES:
        sizes = sorted({row['n'] for row in samples if row['family'] == family})
        for size in sizes:
            group = [row for row in samples if row['family'] == family and row['n'] == size]
            times = [row['wall_seconds'] for row in group]
            wall = statistics.median(times)
            cpu = statistics.median(row['cpu_seconds'] for row in group)
            rss = statistics.median(row['peak_rss_kib'] for row in group) / 1024
            normalized = wall * 1e9 / (size * math.log2(size))
            lines.append(
                f'| {family} | {size} | {wall * 1000:.3f} | '
                f'{min(times) * 1000:.3f}-{max(times) * 1000:.3f} | '
                f'{cpu * 1000:.3f} | {rss:.2f} | {normalized:.2f} |'
            )
    lines.extend(['', 'These observations do not prove an asymptotic bound or establish',
                  'the time and memory available on Mooshak.', ''])
    destination.write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sizes', nargs='+', type=int,
                        default=[10000, 20000, 40000, 80000, 160000, 320000])
    parser.add_argument('--runs', type=int, default=5)
    parser.add_argument('--seed', type=int, default=2026)
    parser.add_argument('--timeout', type=float, default=30)
    parser.add_argument('--output', type=Path, default=ROOT / 'benchmarks' / 'results')
    args = parser.parse_args()
    if platform.system() != 'Linux':
        parser.error('This script uses Linux peak RSS units')
    if args.runs < 1 or args.timeout <= 0 or any(size < 2 for size in args.sizes):
        parser.error('Runs and timeout must be positive; sizes must be at least 2')
    if max(args.sizes) > 1000000:
        parser.error('Keep sizes at most 1,000,000 to limit generated input and memory')

    subprocess.run(['cargo', 'build', '--release'], cwd=ROOT, check=True)
    binary = ROOT / 'target' / 'release' / 'asa_project'
    args.output.mkdir(parents=True, exist_ok=True)
    cpu = next((line.split(':', 1)[1].strip()
                for line in Path('/proc/cpuinfo').read_text().splitlines()
                if line.startswith('model name')), 'unknown')
    metadata = {
        'recorded_at': command_output(['date', '-Iseconds']),
        'platform': platform.platform(),
        'cpu': cpu,
        'logical_cpus': os.cpu_count(),
        'rustc': command_output(['rustc', '--version']),
        'cargo': command_output(['cargo', '--version']),
        'build_command': 'cargo build --release',
        'measurement_compiler': command_output(['cc', '--version']).splitlines()[0],
        'runner_sha256': hashlib.sha256((ROOT / 'benchmarks' / 'runner.c').read_bytes()).hexdigest(),
        'runner_build_command': 'cc -O2 -std=c11 -Wall -Wextra -Werror benchmarks/runner.c -o RUNNER',
        'source_sha256': hashlib.sha256((ROOT / 'src/main.rs').read_bytes()).hexdigest(),
        'binary_sha256': hashlib.sha256(binary.read_bytes()).hexdigest(),
        'seed': args.seed, 'sizes': args.sizes, 'runs': args.runs,
        'timeout_seconds': args.timeout,
        'stdout': '/dev/null', 'warmups_per_dataset': 1,
        'input_sha256': {},
    }
    samples = []
    with tempfile.TemporaryDirectory(prefix='asa-benchmark-') as temporary:
        input_path = Path(temporary) / 'input.txt'
        runner = Path(temporary) / 'runner'
        subprocess.run(['cc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror',
                        str(ROOT / 'benchmarks' / 'runner.c'), '-o', str(runner)], check=True)
        for family in FAMILIES:
            for size in sorted(set(args.sizes)):
                write_input(input_path, family, size, args.seed)
                metadata['input_sha256'][f'{family}/{size}'] = hashlib.sha256(input_path.read_bytes()).hexdigest()
                command = [str(runner), str(binary), str(input_path), str(math.ceil(args.timeout))]
                for run in range(args.runs + 1):
                    result = subprocess.run(command, text=True, capture_output=True,
                                            timeout=args.timeout + 10, check=True)
                    if result.stderr:
                        raise RuntimeError(f'Unexpected solver stderr: {result.stderr}')
                    if run > 0:
                        samples.append({'family': family, 'n': size, 'run': run, **json.loads(result.stdout)})
                print(f'{family}: n={size}, {args.runs} samples recorded', flush=True)

    with (args.output / 'samples.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(samples[0]))
        writer.writeheader()
        writer.writerows(samples)
    (args.output / 'environment.json').write_text(json.dumps(metadata, indent=2) + '\n')
    write_summary(args.output / 'summary.md', samples)
    print(f'Results saved to {args.output}')


if __name__ == '__main__':
    main()
