import pytest

from weather import celsius_to_fahrenheit, fahrenheit_to_celsius, kmh_to_mph


@pytest.mark.parametrize(
    ("celsius", "fahrenheit"),
    [(0, 32), (100, 212), (-40, -40), (37, 98.6)],
)
def test_celsius_to_fahrenheit(celsius: float, fahrenheit: float) -> None:
    assert celsius_to_fahrenheit(celsius) == pytest.approx(fahrenheit)


@pytest.mark.parametrize(
    ("fahrenheit", "celsius"),
    [(32, 0), (212, 100), (-40, -40), (98.6, 37)],
)
def test_fahrenheit_to_celsius(fahrenheit: float, celsius: float) -> None:
    assert fahrenheit_to_celsius(fahrenheit) == pytest.approx(celsius)


@pytest.mark.parametrize("value", [-10.0, 0.0, 21.5, 100.0])
def test_temperature_round_trip(value: float) -> None:
    assert fahrenheit_to_celsius(celsius_to_fahrenheit(value)) == pytest.approx(value)


def test_kmh_to_mph() -> None:
    assert kmh_to_mph(0) == 0
    assert kmh_to_mph(1.609344) == pytest.approx(1)
    assert kmh_to_mph(100) == pytest.approx(62.137, rel=1e-4)


def test_kmh_to_mph_rejects_negative() -> None:
    with pytest.raises(ValueError, match="negative"):
        kmh_to_mph(-1)
