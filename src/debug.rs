use std::time::Instant;

use chrono::Duration;
use hrdf_parser::Hrdf;

use crate::{
    routing::{find_reachable_stops_within_time_limit, plan_journey},
    utils::create_date_time,
};

pub fn run_debug(hrdf: Hrdf) {
    println!();
    println!("------------------------------------------------------------------------------------------------");
    println!("--- Tests");
    println!("------------------------------------------------------------------------------------------------");
    println!();

    println!(
        "{} journeys",
        hrdf.data_storage().journeys().entries().len()
    );

    println!("");

    const ALGORITHM: u32 = 1;

    match ALGORITHM {
        1 => {
            const N: u32 = 10;
            let before = Instant::now();

            for i in 0..N {
                test_plan_journey(&hrdf, i == 0);
            }

            let elapsed = before.elapsed();
            println!("\n{:.2?}", elapsed / N);
        }
        2 => {
            let before = Instant::now();
            test_find_reachable_stops_within_time_limit(&hrdf);
            let elapsed = before.elapsed();
            println!("\n{:.2?}", elapsed);
        }
        _ => panic!(),
    }
}

#[rustfmt::skip]
fn test_plan_journey(hrdf: &Hrdf, verbose: bool) {
    // ------------------------------------------------------------------------------------------------
    // --- 2.0.4
    // ------------------------------------------------------------------------------------------------

    // 8592688     Chancy, Les Bouveries
    // 8592690     Chancy, usine
    // 8587031     Avully, village
    // 8508134     Bernex, Vailly
    // 8587386     Confignon, croisée
    // 8587418     Petit-Lancy, Les Esserts
    // 8592995     Petit-Lancy, Quidort
    // 8587062     Genève, Jonction
    // 8587387     Genève, Bel-Air
    // 8592910     Genève, Terrassière
    // 8587057     Genève, gare Cornavin
    // 8593189     Pont-Céard, gare
    // 8592713     Chêne-Bourg, Place Favre
    // 8588197     Sevelen, Post
    // ...
    // 8501008     Genève
    // 8501120     Lausanne
    // 8768600     Paris Gare de Lyon

    // Chancy, Les Bouveries => Pont-Céard, gare
    // hrdf.plan_journey(8592688, 8593189, create_date_time(2023, 2, 3, 14, 13), verbose);

    // Chancy, Les Bouveries => Chancy, usine
    // hrdf.plan_journey(8592688, 8592690, create_date_time(2023, 2, 3, 14, 2), verbose);

    // Chancy, Les Bouveries => Petit-Lancy, Les Esserts
    // hrdf.plan_journey(8592688, 8587418, create_date_time(2023, 2, 3, 23, 2), verbose);

    // Chancy, Les Bouveries => Genève, Bel-Air
    // hrdf.plan_journey(8592688, 8587387, create_date_time(2023, 2, 3, 14, 31), verbose);

    // Chancy, Les Bouveries => Genève, gare Cornavin
    // hrdf.plan_journey(8592688, 8587057, create_date_time(2023, 2, 3, 12, 55), verbose);
    // hrdf.plan_journey(8592688, 8587057, create_date_time(2023, 2, 3, 14, 31), verbose);
    // hrdf.plan_journey(8592688, 8587057, create_date_time(2023, 2, 3, 20, 40), verbose);
    // hrdf.plan_journey(8592688, 8587057, create_date_time(2023, 2, 3, 21, 40), verbose);

    // Chancy, Les Bouveries => Genève
    // hrdf.plan_journey(8592688, 8501008, create_date_time(2023, 2, 3, 14, 31), verbose);

    // Chancy, Les Bouveries => Lausanne
    // hrdf.plan_journey(8592688, 8501120, create_date_time(2023, 2, 3, 14, 31), verbose);
    // hrdf.plan_journey(8592688, 8501120, create_date_time(2023, 2, 3, 23, 31), verbose);

    // Chancy, Les Bouveries => Sevelen, Post
    // hrdf.plan_journey(8592688, 8588197, create_date_time(2023, 2, 1, 6, 31), verbose);
    // hrdf.plan_journey(8592688, 8588197, create_date_time(2023, 2, 1, 13, 36), verbose);
    // hrdf.plan_journey(8592688, 8588197, create_date_time(2023, 2, 1, 13, 37), verbose); // Worst case I found.
    // hrdf.plan_journey(8592688, 8588197, create_date_time(2023, 2, 1, 14, 31), verbose);
    // hrdf.plan_journey(8592688, 8588197, create_date_time(2023, 2, 1, 18, 31), verbose);

    // ...

    // Confignon, croisée => Petit-Lancy, Les Esserts
    // hrdf.plan_journey(8587386, 8587418, create_date_time(2023, 2, 3, 16, 33), verbose);

    // Petit-Lancy, Les Esserts => Chancy, Les Bouveries
    // hrdf.plan_journey(8587418, 8592688, create_date_time(2023, 2, 3, 23, 33), verbose);

    // Genève => Chancy, Les Bouveries
    // hrdf.plan_journey(8501008, 8592688, create_date_time(2023, 2, 3, 12, 16), verbose);

    // Genève => Genève, Jonction
    // hrdf.plan_journey(8501008, 8587062, create_date_time(2023, 2, 3, 13, 25), verbose);

    // Genève, gare Cornavin => Paris Gare de Lyon
    // hrdf.plan_journey(8587057, 8768600, create_date_time(2023, 2, 3, 13, 25), verbose);

    // ------------------------------------------------------------------------------------------------
    // --- 2.0.5
    // ------------------------------------------------------------------------------------------------

    // hrdf.plan_journey(8592688, 8501120, create_date_time(2024, 2, 3, 14, 31), verbose);
    // hrdf.plan_journey(8592688, 8587057, create_date_time(2024, 2, 3, 14, 39), verbose);
    // hrdf.plan_journey(8592688, 8501008, create_date_time(2024, 9, 10, 14, 39), verbose);
    // hrdf.plan_journey(8592688, 8501008, create_date_time(2024, 9, 10, 14, 39), verbose);
    // hrdf.plan_journey(8592688, 8501008, create_date_time(2024, 9, 10, 22, 30), verbose);
    // hrdf.plan_journey(8592688, 8588197, create_date_time(2024, 9, 10, 13, 37), verbose);
    plan_journey(hrdf, 8592688, 8593189, create_date_time(2024, 2, 3, 14, 13), verbose);
}

fn test_find_reachable_stops_within_time_limit(hrdf: &Hrdf) {
    let routes = find_reachable_stops_within_time_limit(
        hrdf,
        8501008,
        create_date_time(2023, 2, 3, 13, 25),
        Duration::hours(2),
        true,
    );
    println!("\n{}\n", routes.len());
    // routes.get(&8592690).unwrap().print(hrdf.data_storage());
}
