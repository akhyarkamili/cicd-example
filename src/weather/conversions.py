"""Unit conversion helpers."""


def celsius_to_fahrenheit(celsius: float) -> float:
    return celsius * 9 / 5 + 32


def fahrenheit_to_celsius(fahrenheit: float) -> float:
    return (fahrenheit - 32) * 5 / 9


def kmh_to_mph(kmh: float) -> float:
    if kmh < 0:
        raise ValueError("speed cannot be negative")
    return kmh / 1.609344
