import pytest

from weather.cli import main


def test_summary_output(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["London"]) == 0
    out = capsys.readouterr().out
    assert out.startswith("London on ")
    assert "°C" in out


def test_forecast_output_in_fahrenheit(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Tokyo", "--days", "3", "--unit", "f"]) == 0
    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 3
    assert all("°F" in line for line in lines)


def test_unknown_city_exits_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Atlantis"]) == 1
    assert "no weather data" in capsys.readouterr().err


def test_invalid_days_exits_nonzero(capsys: pytest.CaptureFixture[str]) -> None:
    assert main(["Tokyo", "--days", "99"]) == 1
    assert "days must be" in capsys.readouterr().err
