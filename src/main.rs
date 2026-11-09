use std::io::{self, BufWriter, Read, Write};

#[derive(Clone, Copy)]
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

    // Coordinate compression: assign ranks to the distinct base lengths.
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
