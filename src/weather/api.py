"""HTTP API for the dummy weather service.

Run locally with: `uv run uvicorn weather.api:app --reload`
"""

from collections.abc import Iterator
from datetime import date, datetime
from functools import lru_cache
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import Engine, select, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from weather.conversions import celsius_to_fahrenheit
from weather.db import ReadingRecord, get_engine, save_readings
from weather.models import Condition, Reading
from weather.provider import FakeWeatherProvider, UnknownCityError
from weather.service import MAX_FORECAST_DAYS, WeatherService

Unit = Literal["C", "F"]

app = FastAPI(title="cicd-example weather", version="0.1.0")


# --- Dependencies (overridable in tests) -------------------------------------


@lru_cache
def _provider() -> FakeWeatherProvider:
    return FakeWeatherProvider()


def get_service() -> WeatherService:
    return WeatherService(_provider())


@lru_cache
def get_db_engine() -> Engine:
    return get_engine()


def get_session(engine: Annotated[Engine, Depends(get_db_engine)]) -> Iterator[Session]:
    with Session(engine) as session:
        yield session


ServiceDep = Annotated[WeatherService, Depends(get_service)]
SessionDep = Annotated[Session, Depends(get_session)]
UnitQuery = Annotated[Unit, Query(description="temperature unit")]
DaysQuery = Annotated[int, Query(ge=1, le=MAX_FORECAST_DAYS)]


# --- Schemas -----------------------------------------------------------------


class ReadingOut(BaseModel):
    city: str
    day: date
    temperature: float
    unit: Unit
    humidity: int
    wind_kmh: float
    condition: Condition
    is_wet: bool

    @classmethod
    def build(cls, reading: Reading, unit: Unit = "C") -> "ReadingOut":
        return cls(
            city=reading.city,
            day=reading.day,
            temperature=_convert(reading.temperature_c, unit),
            unit=unit,
            humidity=reading.humidity,
            wind_kmh=reading.wind_kmh,
            condition=reading.condition,
            is_wet=reading.is_wet,
        )


class ForecastOut(BaseModel):
    city: str
    unit: Unit
    average_temperature: float
    min_temperature: float
    max_temperature: float
    wet_days: int
    readings: list[ReadingOut]


class SavedReadingOut(BaseModel):
    id: int
    city: str
    day: date
    temperature_c: float
    humidity: int
    wind_kmh: float
    condition: Condition
    created_at: datetime

    model_config = {"from_attributes": True}


class SaveResult(BaseModel):
    saved: int


# --- Helpers -----------------------------------------------------------------


def _convert(celsius: float, unit: Unit) -> float:
    return round(celsius_to_fahrenheit(celsius) if unit == "F" else celsius, 1)


def _not_found(exc: UnknownCityError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc.args[0]))


def _db_unavailable(exc: SQLAlchemyError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"database error: {exc.__class__.__name__}",
    )


# --- Routes ------------------------------------------------------------------


@app.get("/health")
def health(session: SessionDep) -> dict[str, str]:
    try:
        session.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise _db_unavailable(exc) from exc
    return {"status": "ok"}


@app.get("/cities")
def list_cities() -> list[str]:
    return _provider().cities


@app.get("/weather/{city}")
def current_weather(city: str, service: ServiceDep, unit: UnitQuery = "C") -> ReadingOut:
    try:
        return ReadingOut.build(service.current(city), unit)
    except UnknownCityError as exc:
        raise _not_found(exc) from exc


@app.get("/weather/{city}/forecast")
def forecast(
    city: str, service: ServiceDep, days: DaysQuery = 7, unit: UnitQuery = "C"
) -> ForecastOut:
    try:
        fc = service.forecast(city, days)
    except UnknownCityError as exc:
        raise _not_found(exc) from exc
    return ForecastOut(
        city=fc.city,
        unit=unit,
        average_temperature=_convert(fc.average_temperature_c, unit),
        min_temperature=_convert(fc.min_temperature_c, unit),
        max_temperature=_convert(fc.max_temperature_c, unit),
        wet_days=fc.wet_days,
        readings=[ReadingOut.build(r, unit) for r in fc.readings],
    )


@app.post("/weather/{city}/readings", status_code=status.HTTP_201_CREATED)
def save_city_readings(
    city: str,
    service: ServiceDep,
    engine: Annotated[Engine, Depends(get_db_engine)],
    days: DaysQuery = 1,
) -> SaveResult:
    """Generate today's reading (or an N-day forecast) and persist it."""
    try:
        readings = service.forecast(city, days).readings
    except UnknownCityError as exc:
        raise _not_found(exc) from exc
    try:
        return SaveResult(saved=save_readings(engine, readings))
    except SQLAlchemyError as exc:
        raise _db_unavailable(exc) from exc


@app.get("/weather/{city}/readings")
def list_saved_readings(
    city: str,
    session: SessionDep,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
) -> list[SavedReadingOut]:
    stmt = (
        select(ReadingRecord)
        .where(ReadingRecord.city == city.strip().lower())
        .order_by(ReadingRecord.day, ReadingRecord.id)
        .limit(limit)
    )
    try:
        records = session.scalars(stmt).all()
    except SQLAlchemyError as exc:
        raise _db_unavailable(exc) from exc
    return [SavedReadingOut.model_validate(r) for r in records]
