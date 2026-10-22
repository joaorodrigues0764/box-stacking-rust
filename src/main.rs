use std::io::{self, Read};

#[derive(Clone, Copy, Debug)]
struct Orientation {
    width: i32,
    length: i32,
    height: i32,
}

impl Orientation {
    fn new(a: i32, b: i32, h: i32) -> Self {
        if a <= b {
            Self {
                width: a,
                length: b,
                height: h,
            }
        } else {
            Self {
                width: b,
                length: a,
                height: h,
            }
        }
    }
}

fn generate_orientations(a: i32, b: i32, c: i32) -> Vec<Orientation> {
    vec![
        Orientation::new(a, b, c),
        Orientation::new(a, c, b),
        Orientation::new(b, c, a),
    ]
}

fn main() {
    // Ler todo o stdin para uma string
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();

    // Separar por whitespace e converter para inteiros
    let mut values = input
        .split_whitespace()
        .map(|s| s.parse::<i32>().unwrap());

    let n = values.next().unwrap();

    let mut orientations: Vec<Orientation> = Vec::with_capacity((3 * n) as usize);

    for _ in 0..n {
        let a = values.next().unwrap();
        let b = values.next().unwrap();
        let c = values.next().unwrap();

        let block_orientations = generate_orientations(a, b, c);
        orientations.extend(block_orientations);
    }

    // Só para testar se está tudo bem lido
    for o in &orientations {
        println!("{} {} {}", o.width, o.length, o.height);
    }
}