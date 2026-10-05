"""A fake, deterministic weather data provider (no network calls)."""

import hashlib
from datetime import date, timedelta

from weather.models import Condition, Reading

# Baseline climate per city: (mean temperature in C, mean humidity %).
CITY_CLIMATES: dict[str, tuple[float, int]] = {
    "jakarta": (28.0, 80),
    "london": (12.0, 75),
    "new york": (13.0, 63),
    "reykjavik": (5.0, 77),
    "singapore": (27.5, 84),
    "sydney": (18.0, 65),
    "tokyo": (16.0, 65),
}


class UnknownCityError(LookupError):
    """Raised when the provider has no data for the requested city."""


def _seed(city: str, day: date) -> int:
    digest = hashlib.sha256(f"{city}|{day.isoformat()}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


class FakeWeatherProvider:
    """Generates plausible but entirely fake weather readings.

    Output is deterministic for a given (city, day), which keeps tests stable.
    """

    def __init__(self, climates: dict[str, tuple[float, int]] | None = None) -> None:
        self._climates = {k.lower(): v for k, v in (climates or CITY_CLIMATES).items()}

    @property
    def cities(self) -> list[str]:
        return sorted(self._climates)

    def get_reading(self, city: str, day: date) -> Reading:
        key = city.strip().lower()
        if key not in self._climates:
            raise UnknownCityError(f"no weather data for city: {city!r}")

        mean_temp, mean_humidity = self._climates[key]
        seed = _seed(key, day)

        temperature = round(mean_temp + (seed % 101 - 50) / 10, 1)  # +/- 5.0 C
        humidity = max(0, min(100, mean_humidity + (seed >> 8) % 21 - 10))  # +/- 10 %
        wind = round(((seed >> 16) % 400) / 10, 1)  # 0.0 - 39.9 km/h

        conditions = list(Condition)
        if temperature > 2:
            conditions.remove(Condition.SNOWY)
        condition = conditions[(seed >> 24) % len(conditions)]

        return Reading(
            city=key,
            day=day,
            temperature_c=temperature,
            humidity=humidity,
            wind_kmh=wind,
            condition=condition,
        )

    def get_readings(self, city: str, start: date, days: int) -> list[Reading]:
        if days < 1:
            raise ValueError("days must be at least 1")
        return [self.get_reading(city, start + timedelta(days=i)) for i in range(days)]
