# ![Logo](logo.png "Logo") Home Assistant Nutrition Package

Having a smart scale is nice, but nicer if you have a personal health dashboard. 

## Installation

1. Copy `packages/nutrition.yaml` to `/config/packages/nutrition.yaml`.
2. Merge the following into the **existing** `/config/configuration.yaml`:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

3. In Home Assistant, check configuration and restart.
4. Set all inputs to sensible personal values. The BMR coefficient selector is **Male** or **Female** because those are the two published Mifflin-St Jeor offsets.
5. To use the optional YAML dashboard, copy `dashboards/nutrition.yaml` to `/config/dashboards/nutrition.yaml` and merge:

```yaml
lovelace:
  dashboards:
    nutrition-yaml:
      mode: yaml
      title: Nutrition
      icon: mdi:food-apple
      show_in_sidebar: true
      filename: dashboards/nutrition.yaml
```

Do not overwrite any existing `homeassistant:` or `lovelace:` sections. The dashboard is optional; you can instead add the entities to an existing UI-managed dashboard.

## Usage

## Configuration

Single user; manually maintained current weight; no food diary, age auto-update, or data sync. Input selection for BMR uses the binary coefficients of the published equation and is not a statement about gender identity. TDEE is an estimate, not a measured expenditure. This is an informational tool, not medical advice.

BMR uses Mifflin-St Jeor. Activity multiplier is manually supplied, with no claim of precision. Protein and fat targets use current weight. Calorie values use 4 kcal/g for protein and carbohydrates, 9 kcal/g for fat. 
Carbohydrates are marked unavailable if the energy budget cannot cover protein and fat targets.

The 7700 kcal/kg conversion is only a rough static heuristic and ignores metabolic adaptation, water weight and other physiological effects. No goal date is promised. Do not use a computed target as a substitute for personalized dietary guidance. The package does not validate whether a particular deficit or energy intake is appropriate for an individual.

- BMR: Mifflin-St Jeor: `10*kg + 6.25*cm - 5*age + (5 male / -161 female)`.
- TDEE: BMR times user-selected activity factor.
- Calorie target: `max(0, TDEE - daily deficit)`; **not a safety recommendation or minimum calorie target**.
- Protein: current kg times protein factor (g/kg).
- Fat: current kg times fat factor (g/kg).
- Carbs: `(calorie target - 4*protein g - 9*fat g)/4`; unavailable when budget is insufficient.
- Remaining weight: current minus target; positive means above target.
- Estimated days: `remaining kg * 7700 / deficit kcal/day`, available only for weight loss with positive deficit; a crude approximation, not a predicted completion date.


## Contribution

Consider contributing? Check [Contributing](CONTRIBUTING.md) and [Code of Conduct](CODE_OF_CONDUCT.md) beforehand. 

## License

[GNU GPLv3](https://spdx.org/licenses/GPL-3.0-or-later.html)
