from datetime import date

import pytest

from weather import FakeWeatherProvider, WeatherService

FIXED_DAY = date(2026, 1, 15)


@pytest.fixture
def provider() -> FakeWeatherProvider:
    return FakeWeatherProvider()


@pytest.fixture
def service(provider: FakeWeatherProvider) -> WeatherService:
    return WeatherService(provider, today=lambda: FIXED_DAY)
