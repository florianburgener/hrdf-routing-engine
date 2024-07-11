use hrdf_parser::Coordinates;
use serde::Serialize;
use strum_macros::EnumString;

#[derive(Debug, Serialize)]
pub struct IsochroneMap {
    isochrones: Vec<Isochrone>,
    departure_stop_coord: Coordinates,
    bounding_box: ((f64, f64), (f64, f64)),
}

impl IsochroneMap {
    pub fn new(
        isochrones: Vec<Isochrone>,
        departure_stop_coord: Coordinates,
        bounding_box: ((f64, f64), (f64, f64)),
    ) -> Self {
        Self {
            isochrones,
            departure_stop_coord,
            bounding_box,
        }
    }
}

#[derive(Debug, Serialize)]
pub struct Isochrone {
    polygons: Vec<Vec<Coordinates>>,
    time_limit: u32, // In minutes.
}

impl Isochrone {
    pub fn new(polygons: Vec<Vec<Coordinates>>, time_limit: u32) -> Self {
        Self {
            polygons,
            time_limit,
        }
    }
}

#[derive(Debug, EnumString, PartialEq)]
pub enum DisplayMode {
    #[strum(serialize = "circles")]
    Circles,
    #[strum(serialize = "contour_line")]
    ContourLine,
}
