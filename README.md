# HRDF Routing Engine

Public transport routing engine based on Swiss HRDF data.

Author: Florian Burgener

[https://crates.io/crates/hrdf-routing-engine](https://crates.io/crates/hrdf-routing-engine)

## Prerequisites

* OpenSSL (`apt install libssl-dev` on Ubuntu)

## Installation

```sh
git clone https://github.com/florianburgener/hrdf-routing-engine
cd hrdf-routing-engine
```

## Usage

```sh
# Starts debug mode:
cargo run --release
# Starts the web service (port 8100):
cargo run --release -- serve
```
