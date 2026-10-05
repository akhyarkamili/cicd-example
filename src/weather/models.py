"""Domain models for weather data."""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class Condition(StrEnum):
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    STORMY = "stormy"
    SNOWY = "snowy"


@dataclass(frozen=True)
class Reading:
    """A single day's weather reading for a city."""

    city: str
    day: date
    temperature_c: float
    humidity: int
    wind_kmh: float
    condition: Condition

    def __post_init__(self) -> None:
        if not 0 <= self.humidity <= 100:
            raise ValueError(f"humidity must be between 0 and 100, got {self.humidity}")
        if self.wind_kmh < 0:
            raise ValueError(f"wind speed cannot be negative, got {self.wind_kmh}")

    @property
    def is_wet(self) -> bool:
        return self.condition in {Condition.RAINY, Condition.STORMY, Condition.SNOWY}


@dataclass(frozen=True)
class Forecast:
    """A multi-day forecast for a city."""

    city: str
    readings: tuple[Reading, ...]

    def __post_init__(self) -> None:
        if not self.readings:
            raise ValueError("a forecast needs at least one reading")

    @property
    def average_temperature_c(self) -> float:
        return sum(r.temperature_c for r in self.readings) / len(self.readings)

    @property
    def max_temperature_c(self) -> float:
        return max(r.temperature_c for r in self.readings)

    @property
    def min_temperature_c(self) -> float:
        return min(r.temperature_c for r in self.readings)

    @property
    def wet_days(self) -> int:
        return sum(1 for r in self.readings if r.is_wet)
