# cicd-example

A dummy weather project used as a playground for CI/CD. All weather data is fake
and generated deterministically. It makes no network calls. Readings can be saved
to Postgres with `--save`.

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

## Docker

`compose.yaml` runs Postgres, applies Alembic migrations (the one-shot `migrate`
service), then runs the app with `--save`:

```sh
docker compose up --build app
docker compose run --rm app Tokyo --days 5 --save   # run with custom arguments
docker compose exec db psql -U weather -c "select * from readings"
docker compose down -v                               # stop and delete data
```

If port 5432 is already taken on your host, set `POSTGRES_PORT=5433` (or another free port).

## Database migrations (Alembic)

The connection string comes from `DATABASE_URL` (default
`postgresql+psycopg://weather:weather@localhost:5432/weather`).

```sh
docker compose up -d db                                  # Postgres only
uv run alembic upgrade head                              # apply migrations
uv run alembic revision --autogenerate -m "describe change"  # after editing weather/db.py
uv run alembic check                                     # fail if models and migrations differ
```

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
  db.py            # SQLAlchemy models + save_readings
  cli.py           # `weather` command-line entry point
migrations/        # Alembic environment and versions
tests/             # pytest unit tests
```
