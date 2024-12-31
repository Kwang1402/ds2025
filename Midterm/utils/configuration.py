import os
import pathlib
import logging
from typing import Any
import yaml

DEFAULT_PATH = ".configs"
config = {}


def yaml_to_dict(file_path: str):
    with open(file_path, "r", encoding="utf-8") as file:

        d = yaml.load(file, Loader=yaml.FullLoader)
        return d


def get_config_path():
    path = os.environ.get("CONFIG_PATH", DEFAULT_PATH)

    return path


def load_config(config_path: str = None) -> dict[str, Any]:
    config_path = config_path or get_config_path()
    global config

    for root, _, files in os.walk(config_path):
        for file in files:
            if file.endswith(".yaml") or file.endswith(".yml"):
                filepath = os.path.join(root, file)

                data = yaml_to_dict(filepath)
                config |= data

    return config


def get_config() -> dict[str, Any]:
    global config
    config = config or load_config()
    return config
