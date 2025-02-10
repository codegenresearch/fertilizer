import json
import os

from .errors import ConfigKeyError


class Config:
    """
    Class for loading and accessing the config file.
    """

    def __init__(self):
        self._json = {}

    def load_configuration(self, config_filepath: str):
        if not os.path.exists(config_filepath):
            raise FileNotFoundError(f"The configuration file at {config_filepath} does not exist.")

        with open(config_filepath, "r", encoding="utf-8") as f:
            self._json = json.loads(f.read())

        return self

    @property
    def red_key(self) -> str:
        return self._retrieve_key("red_key")

    @property
    def ops_key(self) -> str:
        return self._retrieve_key("ops_key")

    @property
    def server_port(self) -> str:
        return self._retrieve_key("server_port", default="9713")

    def _retrieve_key(self, key, default=None):
        try:
            return self._json[key]
        except KeyError:
            if default is not None:
                return default
            raise ConfigKeyError(f"Key '{key}' not found in the configuration file.")