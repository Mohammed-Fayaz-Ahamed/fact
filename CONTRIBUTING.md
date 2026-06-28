# Contributing to FACT

Thank you for your interest in contributing to FACT.

## Reporting Issues

Before opening an issue, please:

* Search existing issues.
* Provide clear reproduction steps.
* Include Python version and operating system.
* Include logs or stack traces where applicable.

## Development Setup

Clone the repository:

```bash
git clone https://github.com/Mohammed-Fayaz-Ahamed/fact.git
cd fact
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
pip install -e .
```

## Running Tests

```bash
pytest -v
```

## Coding Guidelines

* Follow PEP 8.
* Prefer type hints.
* Keep functions focused and testable.
* Add tests for new functionality.
* Update documentation when behavior changes.

## Pull Requests

Please ensure:

* All tests pass.
* The package builds successfully.
* Documentation is updated when necessary.
* Changes remain backward compatible unless clearly documented.

Thank you for helping improve FACT.
