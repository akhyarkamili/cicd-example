"""Persistence layer: stores weather readings in a SQL database (Postgres in Docker)."""

import os
from collections.abc import Iterable
from datetime import date, datetime

from sqlalchemy import DateTime, Engine, Float, Integer, String, create_engine, func
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from weather.models import Reading

DEFAULT_DATABASE_URL = "postgresql+psycopg://weather:weather@localhost:5432/weather"


class Base(DeclarativeBase):
    pass


class ReadingRecord(Base):
    __tablename__ = "readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    day: Mapped[date]
    temperature_c: Mapped[float] = mapped_column(Float)
    humidity: Mapped[int] = mapped_column(Integer)
    wind_kmh: Mapped[float] = mapped_column(Float)
    condition: Mapped[str] = mapped_column(String(20))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @classmethod
    def from_reading(cls, reading: Reading) -> "ReadingRecord":
        return cls(
            city=reading.city,
            day=reading.day,
            temperature_c=reading.temperature_c,
            humidity=reading.humidity,
            wind_kmh=reading.wind_kmh,
            condition=reading.condition.value,
        )


def database_url() -> str:
    return os.environ.get("DATABASE_URL", DEFAULT_DATABASE_URL)


def get_engine(url: str | None = None) -> Engine:
    return create_engine(url or database_url())


def save_readings(engine: Engine, readings: Iterable[Reading]) -> int:
    records = [ReadingRecord.from_reading(r) for r in readings]
    with Session(engine) as session, session.begin():
        session.add_all(records)
    return len(records)
