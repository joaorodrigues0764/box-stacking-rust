#!/usr/bin/env python3
"""Check the compiled solver against an independent oracle and output validator."""

import argparse
from itertools import combinations_with_replacement, permutations
from pathlib import Path
import random
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def quadratic_height(blocks):
    # Keep all six rotations, without the Rust solver's base normalization.
    rotations = sorted(
        {rotation for block in blocks for rotation in permutations(block)},
        key=lambda block: block[0] * block[1],
    )
    heights = []
    for index, (width, length, height) in enumerate(rotations):
        above = max(
            (
                heights[other]
                for other in range(index)
                if rotations[other][0] < width and rotations[other][1] < length
            ),
            default=0,
        )
        heights.append(height + above)
    return max(heights)


def validate_output(blocks, output, expected_height):
    lines = output.splitlines()
    if not lines:
        raise ValueError('Missing output')

    header = list(map(int, lines[0].split()))
    if len(header) != 2:
        raise ValueError('The first line must contain height and block count')
    height, count = header
    if height <= 0 or count <= 0:
        raise ValueError('Height and block count must be positive')
    if len(lines) != count + 1:
        raise ValueError('The number of block lines does not match the header')
    if height != expected_height:
        raise ValueError(f'Expected optimal height {expected_height}, received {height}')

    allowed = {tuple(sorted(block)) for block in blocks}
    tower = []
    for line in lines[1:]:
        block = tuple(map(int, line.split()))
        if len(block) != 3 or tuple(sorted(block)) not in allowed:
            raise ValueError(f'Invalid block orientation: {line}')
        tower.append(block)

    if sum(block[2] for block in tower) != height:
        raise ValueError('The block heights do not add up to the reported height')
    for bottom, top in zip(tower, tower[1:]):
        if bottom[0] <= top[0] or bottom[1] <= top[1]:
            raise ValueError('Both base dimensions must strictly decrease upwards')


def check_validator():
    blocks = [(5, 10, 20)]
    validate_output(blocks, '25 2\n10 20 5\n5 10 20\n', 25)
    validate_output(blocks, '25 2\n20 10 5\n10 5 20\n', 25)
    invalid_outputs = [
        '',
        '25\n',
        '25 0\n',
        '25 2\n10 20 5\n',
        '24 2\n10 20 5\n5 10 20\n',
        '25 1\n10 20 5\n',
        '25 1\n1 1 25\n',
        '25 2\n5 10 20\n10 20 5\n',
        '40 2\n5 10 20\n5 10 20\n',
    ]
    for output in invalid_outputs:
        expected = 40 if output.startswith('40 ') else 25
        try:
            validate_output(blocks, output, expected)
        except ValueError:
            continue
        raise ValueError(f'The validator accepted invalid output: {output!r}')


def run_case(binary, name, blocks, timeout, expected_height=None):
    data = f'{len(blocks)}\n' + ''.join(f'{a} {b} {c}\n' for a, b, c in blocks)
    try:
        if expected_height is None:
            expected_height = quadratic_height(blocks)
        result = subprocess.run(
            [str(binary)], input=data, text=True, capture_output=True, timeout=timeout
        )
        if result.returncode != 0:
            raise ValueError(f'Exit status {result.returncode}: {result.stderr.strip()}')
        if result.stderr:
            raise ValueError(f'Unexpected stderr: {result.stderr.strip()}')
        validate_output(blocks, result.stdout, expected_height)
    except (ValueError, subprocess.TimeoutExpired) as error:
        failure = ROOT / 'test-cases' / 'failure.in'
        failure.write_text(data)
        raise ValueError(f'{name}: {error}\nReproducer saved to {failure}') from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', type=Path, help='Use an existing executable instead of building')
    parser.add_argument('--seed', type=int, default=2026)
    parser.add_argument('--random-cases', type=int, default=2000)
    parser.add_argument('--timeout', type=float, default=10, help='Seconds allowed per case')
    parser.add_argument('--skip-stress', action='store_true')
    args = parser.parse_args()
    if args.random_cases < 0 or args.timeout <= 0:
        parser.error('Random case count must be nonnegative and timeout must be positive')

    if args.binary is None:
        subprocess.run(['cargo', 'build', '--release'], cwd=ROOT, check=True)
        binary = ROOT / 'target' / 'release' / 'asa_project'
    else:
        binary = args.binary.resolve()

    check_validator()
    count = 0

    def check(name, blocks, expected=None):
        nonlocal count
        run_case(binary, name, blocks, args.timeout, expected)
        count += 1

    fixed_cases = [
        ('first statement example', [(5, 10, 20)], 25),
        ('second statement example', [(2, 2, 2), (1, 3, 3)], 3),
        ('duplicate cubes', [(7, 7, 7)] * 10, 7),
        ('equal short dimensions', [(1, 1, 10)], 10),
        ('equal long dimensions', [(1, 10, 10)], 10),
        ('maximum dimension', [(2147483647,) * 3], 2147483647),
        ('near maximum height', [(1, 2, 2147483646)], 2147483647),
    ]
    for name, blocks, expected in fixed_cases:
        check(name, blocks, expected)
    print('Fixed cases and validator checks passed.', flush=True)

    # Exhaust all multisets of up to three types with dimensions in [1, 3].
    small_types = list(combinations_with_replacement(range(1, 4), 3))
    for size in range(1, 4):
        for blocks in combinations_with_replacement(small_types, size):
            check(f'exhaustive size {size}: {blocks}', blocks)
    print('Exhaustive small cases passed.', flush=True)

    rng = random.Random(args.seed)
    for index in range(args.random_cases):
        size = rng.randint(1, 20)
        if index % 3 == 0:
            blocks = [tuple(rng.randint(1, 5) for _ in range(3)) for _ in range(size)]
        elif index % 3 == 1:
            shared = rng.randint(1, 20)
            blocks = [(shared, rng.randint(1, 40), rng.randint(1, 40)) for _ in range(size)]
        else:
            blocks = [tuple(rng.randint(1, 100) for _ in range(3)) for _ in range(size)]
        check(f'random case {index}, seed {args.seed}', blocks)
        if index % 20 == 0:
            expected = quadratic_height(blocks)
            rng.shuffle(blocks)
            blocks = [tuple(rng.sample(block, 3)) for block in blocks]
            check(f'permuted random case {index}', blocks, expected)
    print(f'Random cases passed (seed {args.seed}).', flush=True)

    if not args.skip_stress:
        size = 60000
        check('long tower', [(side, side, side) for side in range(1, size + 1)],
              size * (size + 1) // 2)
        check('many duplicate types', [(7, 7, 7)] * 100000, 7)
        print('Stress cases passed.', flush=True)

    print(f'All {count} solver cases passed.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(f'FAIL: {error}', file=sys.stderr)
        sys.exit(1)
