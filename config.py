from pathlib import Path
from collections.abc import Mapping
import re

import yaml


CONFIG_FILE = ".worktree-runtime.yml"


def load_config():
    config_path = Path(CONFIG_FILE)

    if not config_path.exists():
        raise FileNotFoundError(
            f"Configuration file '{CONFIG_FILE}' not found."
        )

    with config_path.open("r") as file:
        config = yaml.safe_load(file)

    if not isinstance(config, Mapping):
        raise ValueError("Configuration must be a YAML mapping.")

    ports = config.get("ports")
    commands = config.get("commands")
    if not isinstance(ports, Mapping) or not ports:
        raise ValueError("Configuration must contain a non-empty 'ports' mapping.")
    if not isinstance(commands, Mapping):
        raise ValueError("Configuration must contain a 'commands' mapping.")
    if set(ports) != set(commands):
        raise ValueError("'ports' and 'commands' must define the same services.")

    for service, port_config in ports.items():
        if not isinstance(service, str) or not re.fullmatch(
            r"[A-Za-z_][A-Za-z0-9_-]*", service
        ):
            raise ValueError(
                "Service names must use letters, numbers, underscores, or hyphens."
            )
        if not isinstance(port_config, Mapping):
            raise ValueError(f"Port configuration for '{service}' must be a mapping.")

        start = port_config.get("start")
        end = port_config.get("end")
        if (
            not isinstance(start, int)
            or not isinstance(end, int)
            or not 1 <= start <= end <= 65535
        ):
            raise ValueError(
                f"Port configuration for '{service}' needs a valid start/end range."
            )

        if not isinstance(commands[service], str) or not commands[service].strip():
            raise ValueError(f"Command for '{service}' must be a non-empty string.")

    return config
