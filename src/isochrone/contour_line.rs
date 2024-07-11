use chrono::Duration;
use contour::ContourBuilder;
use hrdf_parser::{CoordinateSystem, Coordinates};

use super::{
    constants::{GRID_SPACING_IN_METERS, WALKING_SPEED_IN_KILOMETERS_PER_HOUR},
    utils::{distance_between_2_points, distance_to_time, lv95_to_wgs84},
};

use rayon::prelude::*;

pub fn create_grid(
    data: &Vec<(Coordinates, Duration)>,
    bounding_box: ((f64, f64), (f64, f64)),
) -> (Vec<(Coordinates, Duration)>, usize, usize) {
    let mut grid = Vec::new();

    let num_points_x =
        ((bounding_box.1 .0 - bounding_box.0 .0) / GRID_SPACING_IN_METERS).ceil() as usize;
    let num_points_y =
        ((bounding_box.1 .1 - bounding_box.0 .1) / GRID_SPACING_IN_METERS).ceil() as usize;

    let mut y = bounding_box.0 .1;
    for _ in 0..num_points_y {
        let mut x = bounding_box.0 .0;

        for _ in 0..num_points_x {
            grid.push(Coordinates::new(CoordinateSystem::LV95, x, y));
            x += GRID_SPACING_IN_METERS;
        }

        y += GRID_SPACING_IN_METERS;
    }

    let grid = grid
        .par_iter()
        .map(|&coord1| {
            let duration = data
                .iter()
                .map(|&(coord2, duration)| {
                    let distance = distance_between_2_points(coord1, coord2);

                    duration + distance_to_time(distance, WALKING_SPEED_IN_KILOMETERS_PER_HOUR)
                })
                .min()
                .unwrap();
            (coord1, duration)
        })
        .collect();
    (grid, num_points_x, num_points_y)
}

pub fn get_polygons(
    grid: &Vec<(Coordinates, Duration)>,
    num_points_x: usize,
    num_points_y: usize,
    min_point: (f64, f64),
    time_limit: Duration,
) -> Vec<Vec<Coordinates>> {
    let values: Vec<_> = grid
        .iter()
        .map(
            |&(_, duration)| {
                if duration <= time_limit {
                    1.0
                } else {
                    0.0
                }
            },
        )
        .collect();

    let contour_builder = ContourBuilder::new(num_points_x, num_points_y, false);
    let contours = contour_builder.contours(&values, &[0.5]).unwrap();

    contours[0]
        .geometry()
        .0
        .iter()
        .map(|polygon| {
            polygon
                .exterior()
                .into_iter()
                .map(|coord| {
                    let lv95 = (
                        min_point.0 + GRID_SPACING_IN_METERS * coord.x,
                        min_point.1 + GRID_SPACING_IN_METERS * coord.y,
                    );
                    let wgs84 = lv95_to_wgs84(lv95.0, lv95.1);
                    Coordinates::new(CoordinateSystem::WGS84, wgs84.0, wgs84.1)
                })
                .collect()
        })
        .collect()
}
