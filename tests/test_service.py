from datetime import date

import pytest

from weather import Condition, Reading, UnknownCityError, WeatherService
from weather.service import MAX_FORECAST_DAYS

from .conftest import FIXED_DAY


class StubProvider:
    """Returns a fixed reading so service behaviour can be tested in isolation."""

    def __init__(self, reading: Reading) -> None:
        self.reading = reading

    def get_reading(self, city: str, day: date) -> Reading:
        return self.reading

    def get_readings(self, city: str, start: date, days: int) -> list[Reading]:
        return [self.reading] * days


def stub_service(condition: Condition = Condition.SUNNY, temp: float = 20.0) -> WeatherService:
    reading = Reading(
        city="london",
        day=FIXED_DAY,
        temperature_c=temp,
        humidity=60,
        wind_kmh=12.34,
        condition=condition,
    )
    return WeatherService(StubProvider(reading), today=lambda: FIXED_DAY)


def test_current_uses_today(service: WeatherService) -> None:
    assert service.current("london").day == FIXED_DAY


def test_current_unknown_city(service: WeatherService) -> None:
    with pytest.raises(UnknownCityError):
        service.current("Atlantis")


def test_forecast_default_length(service: WeatherService) -> None:
    forecast = service.forecast("sydney")
    assert len(forecast.readings) == 7
    assert forecast.city == "sydney"
    assert forecast.readings[0].day == FIXED_DAY


@pytest.mark.parametrize("days", [0, -1, MAX_FORECAST_DAYS + 1])
def test_forecast_rejects_invalid_days(service: WeatherService, days: int) -> None:
    with pytest.raises(ValueError, match="days"):
        service.forecast("sydney", days)


@pytest.mark.parametrize(
    ("condition", "expected"),
    [(Condition.RAINY, True), (Condition.SUNNY, False)],
)
def test_should_bring_umbrella(condition: Condition, expected: bool) -> None:
    assert stub_service(condition=condition).should_bring_umbrella("london") is expected


def test_summary_celsius() -> None:
    assert stub_service(temp=20.0).summary("london") == (
        "London on 2026-01-15: sunny, 20.0°C, humidity 60%, wind 12.3 km/h"
    )


def test_summary_fahrenheit() -> None:
    assert "68.0°F" in stub_service(temp=20.0).summary("london", unit="f")


def test_summary_rejects_unknown_unit() -> None:
    with pytest.raises(ValueError, match="unit"):
        stub_service().summary("london", unit="K")
