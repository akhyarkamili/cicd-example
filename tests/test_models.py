from datetime import date

import pytest

from weather import Condition, Forecast, Reading


def make_reading(
    temperature_c: float = 20.0,
    condition: Condition = Condition.SUNNY,
    humidity: int = 50,
    wind_kmh: float = 10.0,
    day: date = date(2026, 1, 1),
) -> Reading:
    return Reading(
        city="london",
        day=day,
        temperature_c=temperature_c,
        humidity=humidity,
        wind_kmh=wind_kmh,
        condition=condition,
    )


class TestReading:
    @pytest.mark.parametrize("humidity", [-1, 101])
    def test_rejects_invalid_humidity(self, humidity: int) -> None:
        with pytest.raises(ValueError, match="humidity"):
            make_reading(humidity=humidity)

    def test_rejects_negative_wind(self) -> None:
        with pytest.raises(ValueError, match="wind"):
            make_reading(wind_kmh=-0.1)

    @pytest.mark.parametrize("humidity", [0, 100])
    def test_accepts_humidity_bounds(self, humidity: int) -> None:
        assert make_reading(humidity=humidity).humidity == humidity

    @pytest.mark.parametrize(
        ("condition", "expected"),
        [
            (Condition.SUNNY, False),
            (Condition.CLOUDY, False),
            (Condition.RAINY, True),
            (Condition.STORMY, True),
            (Condition.SNOWY, True),
        ],
    )
    def test_is_wet(self, condition: Condition, expected: bool) -> None:
        assert make_reading(condition=condition).is_wet is expected

    def test_is_immutable(self) -> None:
        reading = make_reading()
        with pytest.raises(AttributeError):
            reading.temperature_c = 99  # type: ignore[misc]


class TestForecast:
    def test_requires_readings(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            Forecast(city="london", readings=())

    def test_aggregates(self) -> None:
        forecast = Forecast(
            city="london",
            readings=(
                make_reading(temperature_c=10, condition=Condition.RAINY),
                make_reading(temperature_c=20, condition=Condition.SUNNY),
                make_reading(temperature_c=15, condition=Condition.STORMY),
            ),
        )
        assert forecast.average_temperature_c == pytest.approx(15)
        assert forecast.max_temperature_c == 20
        assert forecast.min_temperature_c == 10
        assert forecast.wet_days == 2
