use std::io::{self, BufWriter, Read, Write};

#[derive(Clone, Copy, Debug)]
struct Orientation {
    width: i32,
    length: i32,
    height: i32,
}

impl Orientation {
    fn new(a: i32, b: i32, height: i32) -> Self {
        Self {
            width: a.min(b),
            length: a.max(b),
            height,
        }
    }
}

fn generate_orientations(a: i32, b: i32, c: i32) -> [Orientation; 3] {
    [
        Orientation::new(a, b, c),
        Orientation::new(a, c, b),
        Orientation::new(b, c, a),
    ]
}

#[derive(Clone, Copy, Default)]
struct BestTower {
    height: i64,
    base: Option<usize>,
}

struct FenwickTree {
    entries: Vec<BestTower>,
}

impl FenwickTree {
    fn new(size: usize) -> Self {
        Self {
            entries: vec![BestTower::default(); size + 1],
        }
    }

    // Return the tallest tower among lengths with ranks from 1 to rank.
    fn query(&self, mut rank: usize) -> BestTower {
        let mut best = BestTower::default();

        while rank > 0 {
            if self.entries[rank].height > best.height {
                best = self.entries[rank];
            }
            rank &= rank - 1;
        }

        best
    }

    fn update(&mut self, mut rank: usize, tower: BestTower) {
        while rank < self.entries.len() {
            if tower.height > self.entries[rank].height {
                self.entries[rank] = tower;
            }
            // Add the lowest set bit to reach the next Fenwick entry.
            let lowest_bit = 1_usize << rank.trailing_zeros();
            rank += lowest_bit;
        }
    }
}

fn tallest_tower(orientations: &mut [Orientation]) -> (i64, Vec<Orientation>) {
    // For equal widths, larger lengths come first. They cannot be selected
    // by a later query for strictly smaller lengths, preventing equal widths
    // from being used together in a tower.
    orientations.sort_unstable_by(|left, right| {
        left.width
            .cmp(&right.width)
            .then_with(|| right.length.cmp(&left.length))
    });

    let mut lengths: Vec<i32> = orientations.iter().map(|block| block.length).collect();
    lengths.sort_unstable();
    lengths.dedup();

    let mut tree = FenwickTree::new(lengths.len());
    let mut next_above = vec![None; orientations.len()];
    let mut best = BestTower::default();

    for (index, block) in orientations.iter().enumerate() {
        // Fenwick ranks start at 1. Excluding this rank enforces strict length.
        let rank = lengths.binary_search(&block.length).unwrap() + 1;
        let above = tree.query(rank - 1);
        next_above[index] = above.base;

        let current = BestTower {
            height: i64::from(block.height) + above.height,
            base: Some(index),
        };

        tree.update(rank, current);
        if current.height > best.height {
            best = current;
        }
    }

    let mut tower = Vec::new();
    let mut current = best.base;

    // Following these links already visits blocks from the base to the top.
    while let Some(index) = current {
        tower.push(orientations[index]);
        current = next_above[index];
    }

    (best.height, tower)
}

fn main() -> io::Result<()> {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input)?;
    let mut values = input.split_whitespace();

    let n: usize = values.next().unwrap().parse().unwrap();
    let mut orientations = Vec::with_capacity(3 * n);

    for _ in 0..n {
        let a = values.next().unwrap().parse().unwrap();
        let b = values.next().unwrap().parse().unwrap();
        let c = values.next().unwrap().parse().unwrap();
        orientations.extend(generate_orientations(a, b, c));
    }

    let (height, tower) = tallest_tower(&mut orientations);
    let stdout = io::stdout();
    let mut output = BufWriter::new(stdout.lock());

    writeln!(output, "{} {}", height, tower.len())?;
    for block in tower {
        writeln!(output, "{} {} {}", block.width, block.length, block.height)?;
    }
    output.flush()
}

#[cfg(test)]
mod tests {
    use super::*;

    fn check_solution(blocks: &[(i32, i32, i32)], expected_height: i64) {
        let mut orientations: Vec<Orientation> = blocks
            .iter()
            .flat_map(|&(a, b, c)| generate_orientations(a, b, c))
            .collect();

        let (height, tower) = tallest_tower(&mut orientations);
        assert_eq!(height, expected_height);
        assert_eq!(
            tower
                .iter()
                .map(|block| i64::from(block.height))
                .sum::<i64>(),
            height
        );

        for pair in tower.windows(2) {
            assert!(pair[0].width > pair[1].width);
            assert!(pair[0].length > pair[1].length);
        }

        for block in tower {
            let mut dimensions = [block.width, block.length, block.height];
            dimensions.sort_unstable();
            assert!(blocks.iter().any(|&(a, b, c)| {
                let mut original = [a, b, c];
                original.sort_unstable();
                original == dimensions
            }));
        }
    }

    fn quadratic_height(blocks: &[(i32, i32, i32)]) -> i64 {
        let mut orientations: Vec<Orientation> = blocks
            .iter()
            .flat_map(|&(a, b, c)| generate_orientations(a, b, c))
            .collect();
        orientations.sort_unstable_by_key(|block| block.width);

        let mut heights = vec![0; orientations.len()];
        for (index, block) in orientations.iter().enumerate() {
            heights[index] = i64::from(block.height);
            for above in 0..index {
                if orientations[above].width < block.width
                    && orientations[above].length < block.length
                {
                    heights[index] = heights[index].max(i64::from(block.height) + heights[above]);
                }
            }
        }
        heights.into_iter().max().unwrap()
    }

    #[test]
    fn statement_examples() {
        check_solution(&[(5, 10, 20)], 25);
        check_solution(&[(2, 2, 2), (1, 3, 3)], 3);
    }

    #[test]
    fn equal_dimensions_cannot_be_stacked() {
        check_solution(&[(7, 7, 7); 10], 7);
        check_solution(&[(1, 1, 10)], 10);
        check_solution(&[(1, 10, 10)], 10);
    }

    #[test]
    fn maximum_dimension_is_supported() {
        check_solution(&[(i32::MAX, i32::MAX, i32::MAX)], i64::from(i32::MAX));
    }

    #[test]
    fn random_cases_match_quadratic_solution() {
        let mut seed = 2026_u64;
        for size in 1..=15 {
            for _ in 0..100 {
                let mut blocks = Vec::new();
                for _ in 0..size {
                    let mut dimensions = [0; 3];
                    for dimension in &mut dimensions {
                        seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
                        *dimension = ((seed >> 32) % 12 + 1) as i32;
                    }
                    blocks.push((dimensions[0], dimensions[1], dimensions[2]));
                }
                check_solution(&blocks, quadratic_height(&blocks));
            }
        }
    }
}
