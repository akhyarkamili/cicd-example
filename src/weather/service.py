"""Application-level weather service."""

from collections.abc import Callable
from datetime import date
from typing import Protocol

from weather.conversions import celsius_to_fahrenheit
from weather.models import Forecast, Reading

MAX_FORECAST_DAYS = 14


class WeatherProvider(Protocol):
    def get_reading(self, city: str, day: date) -> Reading: ...

    def get_readings(self, city: str, start: date, days: int) -> list[Reading]: ...


class WeatherService:
    def __init__(
        self,
        provider: WeatherProvider,
        today: Callable[[], date] = date.today,
    ) -> None:
        self._provider = provider
        self._today = today

    def current(self, city: str) -> Reading:
        return self._provider.get_reading(city, self._today())

    def forecast(self, city: str, days: int = 7) -> Forecast:
        if not 1 <= days <= MAX_FORECAST_DAYS:
            raise ValueError(f"days must be between 1 and {MAX_FORECAST_DAYS}")
        readings = self._provider.get_readings(city, self._today(), days)
        return Forecast(city=readings[0].city, readings=tuple(readings))

    def should_bring_umbrella(self, city: str) -> bool:
        return self.current(city).is_wet

    def summary(self, city: str, unit: str = "C") -> str:
        unit = unit.upper()
        if unit not in {"C", "F"}:
            raise ValueError("unit must be 'C' or 'F'")

        reading = self.current(city)
        temp = reading.temperature_c
        if unit == "F":
            temp = celsius_to_fahrenheit(temp)

        return (
            f"{reading.city.title()} on {reading.day.isoformat()}: "
            f"{reading.condition.value}, {temp:.1f}°{unit}, "
            f"humidity {reading.humidity}%, wind {reading.wind_kmh:.1f} km/h"
        )
