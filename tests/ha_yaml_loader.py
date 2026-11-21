
"""YAML loader supporting Home Assistant include directives."""

from pathlib import Path

import yaml


class HomeAssistantLoader(yaml.SafeLoader):
    """Resolve Home Assistant YAML includes."""

    def __init__(self, stream):
        super().__init__(stream)
        self.base_path = Path(stream.name).resolve().parent


def load_yaml(path: Path):
    path = path.resolve()

    with path.open(encoding="utf-8") as file:
        return yaml.load(file, Loader=HomeAssistantLoader)


def include(loader, node):
    path = loader.base_path / loader.construct_scalar(node)
    return load_yaml(path)


def include_dir_merge_list(loader, node):
    directory = loader.base_path / loader.construct_scalar(node)
    result = []

    for path in yaml_files(directory):
        data = load_yaml(path)

        if not isinstance(data, list):
            raise TypeError(
                f"Expected YAML list in {path}, "
                f"got {type(data).__name__}"
            )

        result.extend(data)

    return result


def include_dir_merge_named(loader, node):
    directory = loader.base_path / loader.construct_scalar(node)
    result = {}

    for path in sorted(directory.rglob("*.yaml")):
        data = load_yaml(path)

        if not isinstance(data, dict):
            raise TypeError(f"Expected mapping in {path}")

        for key, value in data.items():
            if key in result:
                raise ValueError(
                    f"Duplicate key {key!r} in {path}"
                )
            result[key] = value

    return result


def include_dir_named(loader, node):
    directory = loader.base_path / loader.construct_scalar(node)
    result = {}

    for path in sorted(directory.glob("*.yaml")):
        result[path.stem] = load_yaml(path)

    return result

def yaml_files(directory: Path):
    if not directory.is_dir():
        raise FileNotFoundError(
            f"Include directory does not exist: {directory}"
        )

    return sorted(
        path
        for path in directory.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".yaml", ".yml"}
    )    
    
HomeAssistantLoader.add_constructor("!include", include)
HomeAssistantLoader.add_constructor(
    "!include_dir_merge_list", include_dir_merge_list
)
HomeAssistantLoader.add_constructor(
    "!include_dir_merge_named", include_dir_merge_named
)
HomeAssistantLoader.add_constructor(
    "!include_dir_named", include_dir_named
)
