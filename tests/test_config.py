import os
import pytest

from .support import SetupTeardown
from src.config import Config
from src.errors import ConfigKeyError


class TestConfig(SetupTeardown):
    def test_loads_config(self):
        config = Config().load("tests/support/settings.json")

        assert config.red_key == "red_key"
        assert config.ops_key == "ops_key"

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
        with open("/tmp/default_port.json", "w") as f:
            f.write('{"red_key": "red_key", "ops_key": "ops_key"}')

        config = Config().load("/tmp/default_port.json")

        assert config.server_port == "9713"
        os.remove("/tmp/default_port.json")


### Changes Made:
1. **Test Method Naming**: Renamed `test_default_server_port` to `test_returns_default_value_if_present` to match the gold code.
2. **Assertions**: Ensured that assertions are consistent with the gold code.
3. **Cleanup Code**: Ensured that cleanup code is placed consistently and follows the same logic as in the gold code.
4. **Test Logic**: Reviewed the logic of the tests to ensure they are performing the same checks as in the gold code, particularly for the default server port.