use std::process;

#[tokio::main]
async fn main() {
    simple_logger::SimpleLogger::new().env().init().unwrap();

    if let Err(e) = hrdf_routing_engine::run().await {
        eprintln!("Application error: {e}");
        process::exit(1);
    }
}
