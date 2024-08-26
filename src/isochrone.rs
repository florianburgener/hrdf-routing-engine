mod circles;
mod constants;
mod contour_line;
mod models;
mod utils;

use crate::isochrone::utils::haversine_distance;
use crate::routing::find_reachable_stops_within_time_limit;
use crate::routing::RouteResult;
use crate::routing::RouteSectionResult;
use constants::WALKING_SPEED_IN_KILOMETERS_PER_HOUR;
use hrdf_parser::CoordinateSystem;
use hrdf_parser::Coordinates;
use hrdf_parser::DataStorage;
use hrdf_parser::Hrdf;
use hrdf_parser::Model;
use hrdf_parser::Stop;
pub use models::DisplayMode as IsochroneDisplayMode;
pub use models::IsochroneMap;

use chrono::{Duration, NaiveDateTime};

use models::Isochrone;
use utils::distance_to_time;
use utils::lv95_to_wgs84;
use utils::time_to_distance;
use utils::wgs84_to_lv95;

/// Computes the isochrones.
/// The point of origin is used to find the departure stop (the nearest stop).
/// The departure date and time must be within the timetable period.
pub fn compute_isochrones(
    hrdf: &Hrdf,
    origin_point_latitude: f64,
    origin_point_longitude: f64,
    departure_at: NaiveDateTime,
    time_limit: Duration,
    isochrone_interval: Duration,
    display_mode: models::DisplayMode,
    verbose: bool,
) -> IsochroneMap {
    let departure_stop = find_nearest_stop(
        hrdf.data_storage(),
        origin_point_latitude,
        origin_point_longitude,
    );
    let departure_stop_coord = departure_stop.wgs84_coordinates().unwrap();

    // The departure time is calculated according to the time it takes to walk to the departure stop.
    let (adjusted_departure_at, adjusted_time_limit) = adjust_departure_at(
        departure_at,
        time_limit,
        origin_point_latitude,
        origin_point_longitude,
        &departure_stop,
    );

    let mut routes: Vec<_> = find_reachable_stops_within_time_limit(
        hrdf,
        departure_stop.id(),
        adjusted_departure_at,
        adjusted_time_limit,
        verbose,
    )
    .into_iter()
    .filter(|route| {
        // Keeps only stops in Switzerland.
        let stop_id = route.sections().last().unwrap().arrival_stop_id();
        stop_id.to_string().starts_with("85")
    })
    .collect();

    // A false route is created to represent the point of origin in the results.
    let (easting, northing) = wgs84_to_lv95(origin_point_latitude, origin_point_longitude);
    let route = RouteResult::new(
        NaiveDateTime::default(),
        departure_at,
        vec![RouteSectionResult::new(
            None,
            0,
            Some(Coordinates::default()),
            Some(Coordinates::default()),
            0,
            Some(Coordinates::new(CoordinateSystem::LV95, easting, northing)),
            Some(Coordinates::default()),
            Some(NaiveDateTime::default()),
            Some(NaiveDateTime::default()),
            Some(0),
        )],
    );
    routes.push(route);

    let data = get_data(routes, departure_at);
    let bounding_box = get_bounding_box(&data, time_limit);

    let grid = if display_mode == models::DisplayMode::ContourLine {
        Some(contour_line::create_grid(&data, bounding_box, time_limit))
    } else {
        None
    };

    let mut isochrones = Vec::new();
    let isochrone_count = time_limit.num_minutes() / isochrone_interval.num_minutes();

    for i in 0..isochrone_count {
        let time_limit = Duration::minutes(isochrone_interval.num_minutes() * (i + 1));

        let polygons = match display_mode {
            IsochroneDisplayMode::Circles => circles::get_polygons(&data, time_limit),
            IsochroneDisplayMode::ContourLine => {
                let (grid, num_points_x, num_points_y) = grid.as_ref().unwrap();
                contour_line::get_polygons(
                    &grid,
                    *num_points_x,
                    *num_points_y,
                    bounding_box.0,
                    time_limit,
                )
            }
        };

        isochrones.push(Isochrone::new(polygons, time_limit.num_minutes() as u32));
    }

    IsochroneMap::new(
        isochrones,
        departure_stop_coord,
        convert_bounding_box_to_wgs84(bounding_box),
    )
}

fn find_nearest_stop(
    data_storage: &DataStorage,
    origin_point_latitude: f64,
    origin_point_longitude: f64,
) -> &Stop {
    data_storage
        .stops()
        .entries()
        .into_iter()
        // Only considers stops in Switzerland.
        .filter(|stop| stop.id().to_string().starts_with("85"))
        .filter(|stop| stop.wgs84_coordinates().is_some())
        .min_by(|a, b| {
            let coord_1 = a.wgs84_coordinates().unwrap();
            let distance_1 = haversine_distance(
                origin_point_latitude,
                origin_point_longitude,
                coord_1.latitude(),
                coord_1.longitude(),
            );

            let coord_2 = b.wgs84_coordinates().unwrap();
            let distance_2 = haversine_distance(
                origin_point_latitude,
                origin_point_longitude,
                coord_2.latitude(),
                coord_2.longitude(),
            );

            distance_1.partial_cmp(&distance_2).unwrap()
        })
        // The stop list cannot be empty.
        .unwrap()
}

fn adjust_departure_at(
    departure_at: NaiveDateTime,
    time_limit: Duration,
    origin_point_latitude: f64,
    origin_point_longitude: f64,
    departure_stop: &Stop,
) -> (NaiveDateTime, Duration) {
    let distance = {
        let coord = departure_stop.wgs84_coordinates().unwrap();

        haversine_distance(
            origin_point_latitude,
            origin_point_longitude,
            coord.latitude(),
            coord.longitude(),
        ) * 1000.0
    };

    let duration = distance_to_time(distance, WALKING_SPEED_IN_KILOMETERS_PER_HOUR);

    let adjusted_departure_at = departure_at.checked_add_signed(duration).unwrap();
    let adjusted_time_limit = time_limit - duration;

    (adjusted_departure_at, adjusted_time_limit)
}

fn get_data(routes: Vec<RouteResult>, departure_at: NaiveDateTime) -> Vec<(Coordinates, Duration)> {
    routes
        .iter()
        .filter_map(|route| {
            let coord = route
                .sections()
                .last()
                .unwrap()
                .arrival_stop_lv95_coordinates();

            let duration = route.arrival_at() - departure_at;
            coord.zip(Some(duration))
        })
        .collect()
}

fn get_bounding_box(
    data: &Vec<(Coordinates, Duration)>,
    time_limit: Duration,
) -> ((f64, f64), (f64, f64)) {
    let min_x = data
        .iter()
        .fold(f64::INFINITY, |result, &(coord, duration)| {
            let candidate = coord.easting()
                - time_to_distance(time_limit - duration, WALKING_SPEED_IN_KILOMETERS_PER_HOUR);
            f64::min(result, candidate)
        });

    let max_x = data
        .iter()
        .fold(f64::NEG_INFINITY, |result, &(coord, duration)| {
            let candidate = coord.easting()
                + time_to_distance(time_limit - duration, WALKING_SPEED_IN_KILOMETERS_PER_HOUR);
            f64::max(result, candidate)
        });

    let min_y = data
        .iter()
        .fold(f64::INFINITY, |result, &(coord, duration)| {
            let candidate = coord.northing()
                - time_to_distance(time_limit - duration, WALKING_SPEED_IN_KILOMETERS_PER_HOUR);
            f64::min(result, candidate)
        });

    let max_y = data
        .iter()
        .fold(f64::NEG_INFINITY, |result, &(coord, duration)| {
            let candidate = coord.northing()
                + time_to_distance(time_limit - duration, WALKING_SPEED_IN_KILOMETERS_PER_HOUR);
            f64::max(result, candidate)
        });

    ((min_x, min_y), (max_x, max_y))
}

fn convert_bounding_box_to_wgs84(
    bounding_box: ((f64, f64), (f64, f64)),
) -> ((f64, f64), (f64, f64)) {
    (
        lv95_to_wgs84(bounding_box.0 .0, bounding_box.0 .1),
        lv95_to_wgs84(bounding_box.1 .0, bounding_box.1 .1),
    )
}
