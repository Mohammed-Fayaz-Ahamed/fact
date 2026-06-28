# Roadmap

This document outlines the planned evolution of FACT.

The roadmap is intended to communicate the direction of the project. Features listed here are subject to change as the project evolves.

---

# Version 0.1 (Alpha)

The first public release focuses on establishing a reliable, extensible telemetry framework.

Implemented features include:

* FastAPI middleware integration
* Automatic request telemetry collection
* Multi-tenant request support
* Dynamic metadata support
* Payload validation
* Asynchronous in-memory queue
* Background batch processing
* PostgreSQL storage backend
* ClickHouse storage backend
* NoOp storage backend
* Configurable retry mechanism
* Exponential backoff
* Dead Letter Queue (DLQ)
* Runtime telemetry metrics
* Centralized configuration using `FactConfig`
* Environment variable support
* Benchmarking utility
* Automated test suite

---

# Version 0.2

The next milestone focuses on improving observability, extensibility, and operational tooling.

Planned enhancements include:

* Prometheus metrics exporter
* OpenTelemetry integration
* Additional storage backends
* Enhanced benchmark reporting
* Replay support for Dead Letter Queue batches
* Performance optimizations
* Improved logging

---

# Version 0.3

The third milestone focuses on enterprise adoption.

Potential areas include:

* Plugin architecture
* Storage backend registration API
* Custom telemetry processors
* Advanced filtering
* Sampling strategies
* Runtime configuration improvements

---

# Long-Term Vision

FACT aims to become a lightweight and extensible telemetry framework for FastAPI applications.

The long-term goals of the project are:

* Minimal request overhead
* Reliable telemetry persistence
* Backend-independent architecture
* Simple integration
* High-throughput operation
* Clear developer experience
* Comprehensive documentation
* Production-ready reliability

---

# Contributing

Community feedback and contributions are welcome.

As the project evolves, additional contribution guidelines, issue templates, and development workflows will be published.

---

# Release Strategy

FACT follows semantic versioning.

* Major versions introduce breaking changes.
* Minor versions introduce new functionality while maintaining compatibility.
* Patch releases provide bug fixes and stability improvements.

Early releases are intended to gather feedback, validate architectural decisions, and guide future development.
