# Integration Plumbers Rivian Open Telemetry Collector

## Requirements

- [uv](https://docs.astral.sh/uv/) package manager for Python

## Setup

Install `uv`

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh

```

Install `python`

```shell
uv python install 3.14

```

Cloning the repository:

```shell
git clone --recurse-submodules git@github.com:IntegrationPlumbers/ip-rivian-otel-public.git
```

Creating the virtual environment

```shell
uv venv --python 3.14

```
Pin python version

```shell
uv python pin 3.14

```

Install the dependencies
```commandline
uv pip install -r requirements.txt
```

To run the collector
```shell
# From within ip-rivian-otel-public/
uv run main.py

```

## GIT Notes

> **Note**:
> This project utilizes the `rivian-python-api` project as a submodule. It is important that you include `--recurse-submodules` when cloning the project to ensure that you have a fully functional copy.
