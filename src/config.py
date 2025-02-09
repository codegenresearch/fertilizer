import json\nfrom .errors import ConfigKeyError\nclass Config:\n    """\n    Class for loading and accessing the config file.\n    """\n    DEFAULT_SERVER_PORT = "9713"\n    def __init__(self):\n        self._json = {}\n    def load(self, config_filepath: str):\n        if not os.path.exists(config_filepath):\n            raise FileNotFoundError(f"The configuration file at {config_filepath} does not exist.")\n        with open(config_filepath, "r", encoding="utf-8") as f:\n            self._json = json.loads(f.read())\n        return self\n    @property\n    def red_key(self) -> str:\n        return self.__get_key("red_key")\n    @property\n    def ops_key(self) -> str:\n        return self.__get_key("ops_key")\n    @property\n    def server_port(self) -> str:\n        return self._json.get("server_port", self.DEFAULT_SERVER_PORT)\n    def __get_key(self, key):\n        try:\n            return self._json[key]\n        except KeyError:\n            raise ConfigKeyError(f"The key '{key}' is missing from the configuration file. Please ensure it is present.")\n