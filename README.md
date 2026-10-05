# cicd-example

A dummy weather project used as a playground for CI/CD. All weather data is fake
and generated deterministically. It makes no network calls.

## Setup

```sh
uv sync
```

## Usage

```sh
uv run weather London
uv run weather Tokyo --days 5 --unit F
```

Supported cities: Jakarta, London, New York, Reykjavik, Singapore, Sydney, Tokyo.

## Tests

```sh
uv run pytest
```

## Layout

```
src/weather/
  conversions.py   # unit conversions
  models.py        # Reading / Forecast dataclasses
  provider.py      # FakeWeatherProvider (deterministic fake data)
  service.py       # WeatherService (current, forecast, summary)
  cli.py           # `weather` command-line entry point
tests/             # pytest unit tests
```
