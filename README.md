# <img src="./logo.png" alt="Home Assistant Logo" width="32"> Home Assistant Nutrition Package

Having a smart scale is nice, but nicer if you have a personal health dashboard. 

## Installation
1. Copy `packages/nutrition.yaml` to `/config/packages/nutrition.yaml`.
2. Add to your existing configuration, merging with any existing `homeassistant:` section rather than creating a duplicate.
```yaml
homeassistant:
    packages: !include_dir_named packages
``` 
3. Run **Developer Tools > YAML > Check configuration** (location varies by HA version), then restart Home Assistant.
5. Set weight start, goal, macro reference weight, protein and fat factors, and a valid energy budget. Initial zero values are placeholders, not recommended targets.
6. For Garmin, see Configuration section. If Garmin's energy sensor is partial-day, keep manual energy mode enabled.
7. To use the example Lovelace dashboard, create a dashboard and paste the contents of `dashboards/nutrition.yaml`, or adapt its cards to your existing dashboard.

Entity IDs can be changed by Home Assistant if conflicts or registry history exist. Confirm the actual IDs in Developer Tools > States before using the example dashboard.

## Usage

- Weight lost (kg): `start - current`. Negative values indicate weight gain.
- Weight remaining (kg): `max(current - goal, 0)` for loss goals; `max(goal - current, 0)` for gain goals.
- Progress (%): `clamp(100 × (current - start) / (goal - start), 0, 100)`; undefined when start equals goal.
- Deficit (kcal): `daily_energy × deficit_percent / 100`.
- Calorie target (kcal): `daily_energy - deficit`.
- Protein (g): `reference_weight × protein_factor`.
- Fat (g): `reference_weight × fat_factor`.
- Carbs (g): `max((calorie_target - 4 × protein_g - 9 × fat_g) / 4, 0)`.
- Macro budget feasible: calorie target is at least the combined protein and fat energy.

These are simplified planning formulas. An estimated daily energy budget is not the same as live partial-day burned calories. The deficit input supports only nonnegative deficits; weight-gain goals can still be tracked, but a calorie surplus mode is not implemented in v1.

# Configuration

## Garmin Connect example

Supported Sources:

- Weight: `sensor.garmin_connect_weight` (kg)
- Energy: `sensor.garmin_connect_burned_calories` (kcal)

These entity IDs are pre-populated in the two `input_text` helpers. Weight can be used directly if the Garmin entity returns kg. The energy sensor may **only** be used as a daily budget if it tracks total daily energy expenditure and does not include a running counter for the day so far. Until this is clarified, leave `input_boolean.nutrition_manual_energy` enabled and set the daily budget manually.

BMR example: set `input_text.nutrition_bmr_source` to `sensor.garmin_connect_bmr_calories` and leave `input_boolean.nutrition_manual_bmr` off. Verify this is comparable to the **full-day** energy estimate; do not mix a running total with a full-day BMR.

The actual sensor IDs depend on the Garmin integration and may differ. Confirm them in Developer Tools > States.

## Manual-only example

Turn on both `input_boolean.nutrition_manual_weight` and `input_boolean.nutrition_manual_energy`. Enter weight in kg and a full-day energy estimate in kcal using their corresponding `input_number` helpers. No fitness or smart-scale integration is required.


## Data adapters

`input_text.nutrition_weight_source`: entity ID for numeric weight in kg. Default example: `sensor.garmin_connect_weight`.

`input_text.nutrition_energy_source`: entity ID for numeric **complete daily** energy expenditure/budget in kcal/day. Default example: `sensor.garmin_connect_burned_calories`, **not automatically safe to use**.

Enable `input_boolean.nutrition_manual_weight` to read `input_number.nutrition_manual_weight_kg` instead of the weight source.

Enable `input_boolean.nutrition_manual_energy` to read `input_number.nutrition_manual_daily_energy` instead of the energy source. This switch starts enabled.

## Goal and macro inputs

- `input_number.weight_start`: starting weight (kg)
- `input_number.weight_goal`: goal weight (kg)
- `input_number.target_calorie_deficit`: calorie deficit percentage, 0–30
- `input_number.nutrition_reference_weight`: macro reference weight (kg), independently configurable
- `input_number.nutrition_protein_factor`: protein g/kg
- `input_number.nutrition_fat_factor`: fat g/kg

The package does not automatically update start or reference weight. Set them intentionally.

## Reliability

Unavailable source data yields an unavailable template sensor rather than a misleading zero. No conversion is performed; verify source units. Templates refer to stable internal sensor IDs, not integration-specific IDs. If an entity ID has been customized in the registry, update dependent templates accordingly.


## Contribution

Consider contributing? Check [Contributing](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) beforehand. 

## License

[GNU GPLv3](https://spdx.org/licenses/GPL-3.0-or-later.html)
