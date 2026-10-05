from datetime import date, timedelta

import pytest

from weather import Condition, FakeWeatherProvider, UnknownCityError

DAY = date(2026, 1, 15)


def test_lists_known_cities(provider: FakeWeatherProvider) -> None:
    assert "london" in provider.cities
    assert provider.cities == sorted(provider.cities)


def test_reading_is_deterministic(provider: FakeWeatherProvider) -> None:
    assert provider.get_reading("London", DAY) == provider.get_reading("London", DAY)


def test_city_lookup_is_case_and_whitespace_insensitive(
    provider: FakeWeatherProvider,
) -> None:
    assert provider.get_reading("  LoNdOn ", DAY) == provider.get_reading("london", DAY)


def test_unknown_city_raises(provider: FakeWeatherProvider) -> None:
    with pytest.raises(UnknownCityError, match="Atlantis"):
        provider.get_reading("Atlantis", DAY)


@pytest.mark.parametrize("city", FakeWeatherProvider().cities)
def test_readings_are_within_plausible_ranges(provider: FakeWeatherProvider, city: str) -> None:
    for reading in provider.get_readings(city, DAY, 30):
        assert 0 <= reading.humidity <= 100
        assert 0 <= reading.wind_kmh < 40
        assert -50 < reading.temperature_c < 60
        if reading.temperature_c > 2:
            assert reading.condition is not Condition.SNOWY


def test_get_readings_returns_consecutive_days(provider: FakeWeatherProvider) -> None:
    readings = provider.get_readings("tokyo", DAY, 5)
    assert [r.day for r in readings] == [DAY + timedelta(days=i) for i in range(5)]


def test_get_readings_rejects_zero_days(provider: FakeWeatherProvider) -> None:
    with pytest.raises(ValueError):
        provider.get_readings("tokyo", DAY, 0)


def test_custom_climates() -> None:
    provider = FakeWeatherProvider({"Antarctica": (-30.0, 50)})
    assert provider.cities == ["antarctica"]
    reading = provider.get_reading("antarctica", DAY)
    assert -35 <= reading.temperature_c <= -25
