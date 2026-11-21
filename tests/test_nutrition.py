
"""Contract tests for the actual Home Assistant Jinja templates.

Run from the repository root:
    python -m pytest -q
"""

from datetime import datetime, timedelta
from pathlib import Path
import math

import pytest
from jinja2 import Environment, StrictUndefined

from tests.ha_yaml_loader import load_yaml


PACKAGE = (
    Path(__file__).resolve().parents[1]
    / "packages"
    / "nutrition.yaml"
)


DEFAULT = {
    "input_number.weight_start": "100",
    "input_number.weight_goal": "80",
    "sensor.nutrition_weight": "90",
    "sensor.nutrition_energy_expenditure": "2500",
    "input_number.target_calorie_deficit": "20",
    "sensor.target_calorie_deficit": "500",
    "sensor.estimated_days_to_weight_goal": "77",
}

def test_debug_templates():
    data = load_yaml(PACKAGE)

    print("\nTemplate data:")
    print(repr(data.get("template")))

    assert data.get("template")

@pytest.fixture(scope="module")
def sensors():
    """Load all template sensors from the modular package."""
    data = load_yaml(PACKAGE)

    result = {}

    for group in data["template"]:
        for sensor in group.get("sensor", []):
            name = sensor["name"]

            if name in result:
                raise ValueError(
                    f"Duplicate template sensor: {name}"
                )

            result[name] = sensor

    return result


def render(sensor, field="state", overrides=None):
    """Render a Home Assistant Jinja template with mocked states."""
    values = {**DEFAULT, **(overrides or {})}

    def states(entity):
        return values.get(entity, "unknown")

    def is_number(value):
        try:
            return math.isfinite(float(value))
        except (ValueError, TypeError):
            return False

    def ha_float(value, default=None):
        try:
            number = float(value)

            if not math.isfinite(number):
                raise ValueError

            return number

        except (ValueError, TypeError):
            if default is None:
                raise ValueError(
                    f"Invalid float: {value!r}"
                )

            return default

    def ha_int(value, default=None):
        try:
            number = float(value)

            if not math.isfinite(number):
                raise ValueError

            return int(number)

        except (ValueError, TypeError):
            if default is None:
                raise ValueError(
                    f"Invalid int: {value!r}"
                )

            return default

    environment = Environment(
        undefined=StrictUndefined,
        autoescape=False,
    )

    environment.filters["float"] = ha_float
    environment.filters["int"] = ha_int

    environment.globals.update(
        states=states,
        is_number=is_number,
        today_at=lambda: datetime(2026, 10, 11),
        timedelta=timedelta,
    )

    return (
        environment
        .from_string(sensor[field])
        .render()
        .strip()
    )


def available(sensor, overrides=None):
    """Evaluate a sensor's availability template."""
    return (
        render(sensor, "availability", overrides).lower()
        == "true"
    )


# ---------------------------------------------------------
# Package contract tests
# ---------------------------------------------------------

def test_required_sensors_exist(sensors):
    expected = {
        "Weight Goal Progress",
        "Target Calorie Deficit",
        "Estimated Days to Weight Goal",
        "Estimated Weight Goal Date",
    }

    assert expected <= sensors.keys()


def test_sensors_have_unique_ids(sensors):
    ids = [
        sensor["unique_id"]
        for sensor in sensors.values()
    ]

    assert len(ids) == len(set(ids))


def test_sensors_have_states(sensors):
    for name, sensor in sensors.items():
        assert "state" in sensor, (
            f"Sensor {name!r} has no state template"
        )


# ---------------------------------------------------------
# Weight goal progress - weight loss
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "current,goal,expected",
    [
        ("90", "80", 50.0),
        ("80", "80", 100.0),
        ("105", "80", 0.0),
        ("70", "80", 100.0),
    ],
)
def test_weight_progress_loss(
    sensors, current, goal, expected
):
    sensor = sensors["Weight Goal Progress"]

    values = {
        "sensor.nutrition_weight": current,
        "input_number.weight_goal": goal,
    }

    assert available(sensor, values)

    assert float(
        render(sensor, overrides=values)
    ) == pytest.approx(expected)


# ---------------------------------------------------------
# Weight goal progress - weight gain
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "current,expected",
    [
        ("90", 50),
        ("100", 100),
        ("75", 0),
    ],
)
def test_weight_progress_gain(
    sensors, current, expected
):
    sensor = sensors["Weight Goal Progress"]

    values = {
        "input_number.weight_start": "80",
        "input_number.weight_goal": "100",
        "sensor.nutrition_weight": current,
    }

    assert available(sensor, values)

    assert float(
        render(sensor, overrides=values)
    ) == pytest.approx(expected)


def test_progress_equal_start_goal_unavailable(sensors):
    sensor = sensors["Weight Goal Progress"]

    assert not available(
        sensor,
        {"input_number.weight_goal": "100"},
    )


# ---------------------------------------------------------
# Target calorie deficit
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "energy,percent,expected",
    [
        ("2500", "20", 500),
        ("2500", "0", 0),
        ("2000", "15", 300),
    ],
)
def test_deficit(
    sensors, energy, percent, expected
):
    sensor = sensors["Target Calorie Deficit"]

    values = {
        "sensor.nutrition_energy_expenditure": energy,
        "input_number.target_calorie_deficit": percent,
    }

    assert available(sensor, values)

    assert float(
        render(sensor, overrides=values)
    ) == pytest.approx(expected)


@pytest.mark.parametrize(
    "invalid",
    [
        "unknown",
        "unavailable",
        "",
    ],
)
def test_deficit_missing_source(sensors, invalid):
    sensor = sensors["Target Calorie Deficit"]

    assert not available(
        sensor,
        {
            "sensor.nutrition_energy_expenditure": invalid
        },
    )


# ---------------------------------------------------------
# Estimated days to weight goal
# ---------------------------------------------------------

@pytest.mark.parametrize(
    "weight,goal,deficit,expected",
    [
        ("85", "80", "500", 77),
        ("80", "80", "500", 0),
        ("78", "80", "500", 0),
        ("90", "80", "770", 100),
    ],
)
def test_estimated_days(
    sensors, weight, goal, deficit, expected
):
    sensor = sensors["Estimated Days to Weight Goal"]

    values = {
        "sensor.nutrition_weight": weight,
        "input_number.weight_goal": goal,
        "sensor.target_calorie_deficit": deficit,
    }

    assert available(sensor, values)

    assert int(
        render(sensor, overrides=values)
    ) == expected


@pytest.mark.parametrize(
    "deficit",
    [
        "0",
        "unknown",
        "unavailable",
    ],
)
def test_estimated_days_without_deficit(
    sensors, deficit
):
    sensor = sensors["Estimated Days to Weight Goal"]

    values = {
        "sensor.nutrition_weight": "85",
        "input_number.weight_goal": "80",
        "sensor.target_calorie_deficit": deficit,
    }

    assert not available(sensor, values)


# ---------------------------------------------------------
# Estimated weight goal date
# ---------------------------------------------------------

def test_estimated_date(sensors):
    sensor = sensors["Estimated Weight Goal Date"]

    assert available(sensor)

    assert render(sensor) == "2026-12-27"


def test_estimated_date_unavailable_without_days(sensors):
    sensor = sensors["Estimated Weight Goal Date"]

    assert not available(
        sensor,
        {
            "sensor.estimated_days_to_weight_goal":
                "unavailable"
        },
    )
