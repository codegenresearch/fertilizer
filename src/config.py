import json

from .errors import ConfigKeyError


class Config:
  """\n  Class for loading and accessing the config file.\n  """

  def __init__(self):
    self._json = {}
    self._server_port = "9713"  # Default server port

  def load(self, config_filepath: str):
    if not os.path.exists(config_filepath):
      raise FileNotFoundError(f"{config_filepath} does not exist.")

    with open(config_filepath, "r", encoding="utf-8") as f:
      self._json = json.loads(f.read())

    return self

  @property
  def red_key(self) -> str:
    return self.__get_key("red_key")

  @property
  def ops_key(self) -> str:
    return self.__get_key("ops_key")

  @property
  def server_port(self) -> str:
    return self._server_port

  def __get_key(self, key):
    try:
      return self._json[key]
    except KeyError:
      raise ConfigKeyError(f"Key '{key}' not found in config file.")