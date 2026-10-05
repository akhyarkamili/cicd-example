from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine

from tests.conftest import FIXED_DAY
from weather.api import app, get_db_engine, get_service
from weather.db import Base, get_engine
from weather.provider import FakeWeatherProvider
from weather.service import WeatherService


@pytest.fixture
def engine(tmp_path: Path) -> Engine:
    engine = get_engine(f"sqlite:///{tmp_path / 'weather.db'}")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def client(engine: Engine) -> Iterator[TestClient]:
    app.dependency_overrides[get_service] = lambda: WeatherService(
        FakeWeatherProvider(), today=lambda: FIXED_DAY
    )
    app.dependency_overrides[get_db_engine] = lambda: engine
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_cities(client: TestClient) -> None:
    resp = client.get("/cities")
    assert resp.status_code == 200
    assert "london" in resp.json()


def test_current_weather(client: TestClient) -> None:
    resp = client.get("/weather/London")
    assert resp.status_code == 200
    body = resp.json()
    assert body["city"] == "london"
    assert body["day"] == FIXED_DAY.isoformat()
    assert body["unit"] == "C"


def test_current_weather_in_fahrenheit(client: TestClient) -> None:
    c = client.get("/weather/London").json()["temperature"]
    f = client.get("/weather/London", params={"unit": "F"}).json()["temperature"]
    assert f == round(c * 9 / 5 + 32, 1)


def test_unknown_city_is_404(client: TestClient) -> None:
    resp = client.get("/weather/Atlantis")
    assert resp.status_code == 404
    assert "no weather data" in resp.json()["detail"]


@pytest.mark.parametrize("params", [{"unit": "K"}, {"days": 0}, {"days": 99}])
def test_invalid_query_is_422(client: TestClient, params: dict[str, str | int]) -> None:
    assert client.get("/weather/Tokyo/forecast", params=params).status_code == 422


def test_forecast(client: TestClient) -> None:
    resp = client.get("/weather/Tokyo/forecast", params={"days": 3})
    assert resp.status_code == 200
    body = resp.json()
    assert len(body["readings"]) == 3
    assert body["min_temperature"] <= body["average_temperature"] <= body["max_temperature"]


def test_save_and_list_readings(client: TestClient) -> None:
    resp = client.post("/weather/Tokyo/readings", params={"days": 3})
    assert resp.status_code == 201
    assert resp.json() == {"saved": 3}

    saved = client.get("/weather/tokyo/readings").json()
    assert [r["city"] for r in saved] == ["tokyo"] * 3
    assert saved[0]["day"] == FIXED_DAY.isoformat()
    assert client.get("/weather/London/readings").json() == []


def test_save_unknown_city_is_404(client: TestClient) -> None:
    assert client.post("/weather/Atlantis/readings").status_code == 404


def test_db_errors_are_503(tmp_path: Path, client: TestClient) -> None:
    # A database with no tables, i.e. migrations not run.
    empty = get_engine(f"sqlite:///{tmp_path / 'empty.db'}")
    app.dependency_overrides[get_db_engine] = lambda: empty
    assert client.post("/weather/London/readings").status_code == 503
    assert client.get("/weather/London/readings").status_code == 503
