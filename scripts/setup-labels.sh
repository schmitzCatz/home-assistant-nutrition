#!/usr/bin/env bash
set -euo pipefail
# Requires GitHub CLI (gh auth login), run at the repository root.
while IFS='|' read -r name color description; do
  [[ -z "$name" || "$name" == \#* ]] && continue
  gh label create "$name" --color "$color" --description "$description" --force
done <<'LABELS'
area:weight|1D76DB|Weight goals and progress
area:energy|FBCA04|Energy expenditure and calorie targets
area:macros|5319E7|Protein fat and carbohydrate calculations
area:dashboard|0E8A16|Lovelace dashboard
area:ci|0052CC|Continuous integration and tests
priority:high|B60205|High priority
priority:medium|D93F0B|Medium priority
priority:low|C2E0C6|Low priority
LABELS
