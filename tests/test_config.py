import os
import pytest

from .support import SetupTeardown

from src.config import Config
from src.errors import ConfigKeyError


class TestConfig(SetupTeardown):
    def test_loads_config(self):
        config = Config().load("tests/support/settings.json")

        assert config.red_key == "secret_red"
        assert config.ops_key == "secret_ops"
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

    def test_uses_default_server_port_when_not_specified(self):
        with open("/tmp/default_port.json", "w") as f:
            f.write('{"red_key": "secret_red", "ops_key": "secret_ops"}')

        config = Config().load("/tmp/default_port.json")

        assert config.server_port == "9713"
        os.remove("/tmp/default_port.json")

    def test_uses_custom_server_port_when_specified(self):
        with open("/tmp/custom_port.json", "w") as f:
            f.write('{"red_key": "secret_red", "ops_key": "secret_ops", "port": "8080"}')

        config = Config().load("/tmp/custom_port.json")

        assert config.server_port == "8080"
        os.remove("/tmp/custom_port.json")