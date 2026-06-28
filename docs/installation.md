# Installation

This guide explains how to install, configure, and run FACT in a development environment.

---

## Prerequisites

Before installing FACT, ensure the following software is available:

* Python 3.10 or later
* Git
* pip
* Virtual environment support (`venv`)

Optional storage backends:

* PostgreSQL
* ClickHouse

---

## Clone the Repository

```bash
git clone <repository-url>
cd fact
```

---

## Create a Virtual Environment

Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Configure FACT

FACT loads its configuration through the `FactConfig` class. By default, configuration values can also be supplied using environment variables.

Example:

```bash
export FACT_STORAGE_BACKEND=noop
```

Supported storage backends:

* `noop`
* `postgres`
* `clickhouse`

---

## Running the Example Application

Start the example FastAPI application:

```bash
uvicorn examples.main:app --workers 4
```

The application will be available at:

```
http://127.0.0.1:8000
```

---

## Running the Test Suite

Execute the complete automated test suite:

```bash
python3 -m pytest -v
```

All tests should pass before submitting changes or publishing a release.

---

## Running the Benchmark

Execute the benchmark utility:

```bash
python3 scripts/benchmark.py --requests 10000 --concurrency 50
```

The benchmark reports:

* Throughput
* Average latency
* P50 latency
* P95 latency
* P99 latency
* Success rate
* Server error rate
* Transport failure rate
* Tenant request distribution

---

## Next Steps

After successfully installing FACT:

1. Read the Quick Start guide.
2. Configure the desired storage backend.
3. Integrate the middleware into your FastAPI application.
4. Explore the benchmarking and runtime metrics capabilities.
