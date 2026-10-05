"""A dummy weather package used to demonstrate CI/CD."""

from weather.conversions import celsius_to_fahrenheit, fahrenheit_to_celsius, kmh_to_mph
from weather.models import Condition, Forecast, Reading
from weather.provider import FakeWeatherProvider, UnknownCityError
from weather.service import WeatherService

__all__ = [
    "Condition",
    "FakeWeatherProvider",
    "Forecast",
    "Reading",
    "UnknownCityError",
    "WeatherService",
    "celsius_to_fahrenheit",
    "fahrenheit_to_celsius",
    "kmh_to_mph",
]
