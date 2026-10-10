from pathlib import Path
import yaml

root = Path(__file__).resolve().parents[1]
for file in sorted(root.rglob('*.yaml')):
    with file.open(encoding='utf-8') as stream:
        yaml.safe_load(stream)
    print('OK', file.relative_to(root))
print('YAML syntax checks passed; Home Assistant runtime validation is still required.')
