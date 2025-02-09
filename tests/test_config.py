import os
import pytest

from .support import SetupTeardown
from src.config import Config, ConfigKeyError


class TestConfig(SetupTeardown):
    def test_loads_config_with_correct_values(self):
        config = Config().load("tests/support/settings.json")

        assert config.red_key == "red_key"
        assert config.ops_key == "ops_key"
        assert config.server_port == "9713"

    def test_raises_error_on_missing_config_file(self):
        with pytest.raises(FileNotFoundError) as excinfo:
            Config().load("tests/support/missing.json")

        assert "tests/support/missing.json does not exist" in str(excinfo.value)

    def test_raises_error_on_missing_key_without_default(self):
        with open("/tmp/empty.json", "w") as f:
            f.write("{}")

        config = Config().load("/tmp/empty.json")

        with pytest.raises(ConfigKeyError) as excinfo:
            config.red_key

        assert "Key 'red_key' not found in config file." in str(excinfo.value)
        os.remove("/tmp/empty.json")

    def test_returns_default_value_if_present(self):
        with open("/tmp/default.json", "w") as f:
            f.write('{"port": "1234"}')

        config = Config().load("/tmp/default.json")

        assert config.server_port == "1234"
        os.remove("/tmp/default.json")