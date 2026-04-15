# Integration Plumbers Rivian Open Telemetry Collector

A simple demonstration of an OpenTelemetry (OTLP) collector for Rivian vehicle data in Python. It polls a Rivian account via the [`rivian-python-api`](https://github.com/the-mace/rivian-python-api) library (included as a git submodule) and exports metrics over OTLP/HTTP to a backend such as Prometheus.

## Metrics Collected

On each polling cycle (default: every 90 seconds) the collector publishes gauges for the first vehicle returned by the Rivian API:

- `riv_lf_tire_status_good` / `riv_lf_tire_status_bad` — Left Front tire pressure OK/LOW
- `riv_rf_tire_status_good` / `riv_rf_tire_status_bad` — Right Front tire pressure OK/LOW
- `riv_lr_tire_status_good` / `riv_lr_tire_status_bad` — Left Rear tire pressure OK/LOW
- `riv_rr_tire_status_good` / `riv_rr_tire_status_bad` — Right Rear tire pressure OK/LOW
- `riv_battery_level` — raw battery level reported by the vehicle
- `riv_battery_percentage` — battery level as a percentage of capacity
- `riv_charger_state` — `1` when the charger is connected, `0` otherwise

The collector additionally retrieves live charging session data and completed charge session summaries (for future use / inspection).

## Requirements

- [uv](https://docs.astral.sh/uv/) package manager for Python
- Python 3.14 (enforced by `pyproject.toml` and `.python-version`)
- An OTLP/HTTP-compatible metrics backend (e.g. Prometheus with the OTLP receiver enabled)

## Setup

Install `uv`:

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repository (the `--recurse-submodules` flag is **required** to pull in `rivian-python-api`):

```shell
git clone --recurse-submodules git@github.com:IntegrationPlumbers/ip-rivian-otel-public.git
cd ip-rivian-otel-public
```

Install Python 3.14:

```shell
uv python install 3.14
```

Pin the Python version and create the virtual environment:

```shell
uv python pin 3.14
uv venv --python 3.14
```

Install the dependencies:

```shell
uv pip install -r requirements.txt
```

## Running

From the repository root:

```shell
uv run rivian_collector.py
```

The collector runs until interrupted (Ctrl-C) and on shutdown cleanly flushes the OpenTelemetry `MeterProvider`.

## Configuration

The OTLP endpoint is currently **hardcoded** in `ip_rivian_otel/__main__.py` via the `main()` function:

```python
endpoint = "http://prometheus.ip:9090//api/v1/otlp/v1/metrics"
```

Edit this value to point at your own OTLP/HTTP metrics receiver. The polling interval (default `90` seconds) is passed to `IPRivianOTLP.collect()` from the same function.

Rivian account credentials are handled by the `rivian-python-api` submodule — consult its documentation for the authentication flow it expects.

## GIT Notes

> **Note**:
> This project utilizes the `rivian-python-api` project as a submodule. It is important that you include `--recurse-submodules` when cloning the project to ensure that you have a fully functional copy. If you already cloned without it, run:
>
> ```shell
> git submodule update --init --recursive
> ```
