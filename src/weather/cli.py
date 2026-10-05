"""Command-line entry point: `weather <city> [--days N] [--unit C|F]`."""

import argparse
import sys

from weather.conversions import celsius_to_fahrenheit
from weather.provider import FakeWeatherProvider, UnknownCityError
from weather.service import WeatherService


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="weather", description="Dummy weather reports.")
    parser.add_argument("city", help="city name, e.g. 'London'")
    parser.add_argument("--days", type=int, default=0, help="show an N-day forecast")
    parser.add_argument("--unit", choices=["C", "F"], default="C", type=str.upper)
    args = parser.parse_args(argv)

    service = WeatherService(FakeWeatherProvider())

    try:
        if args.days:
            forecast = service.forecast(args.city, args.days)
            for r in forecast.readings:
                temp = r.temperature_c
                if args.unit == "F":
                    temp = celsius_to_fahrenheit(temp)
                print(f"{r.day.isoformat()}  {temp:5.1f}°{args.unit}  {r.condition.value}")
        else:
            print(service.summary(args.city, args.unit))
    except (UnknownCityError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
