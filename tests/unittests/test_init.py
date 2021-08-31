import os
import unittest
from unittest.mock import patch, call

from libheysops.base import CONFIG_TEMPLATE
from libheysops.init.init import Init


class TestInit(unittest.TestCase):
    @patch("libheysops.init.init.os")
    @patch("libheysops.init.init.open")
    def test_create_config1(self, mock_open, mock_os):
        mock_os.path.isdir.return_value = True
        mock_os.path.exists.return_value = False
        mock_os.path.join = os.path.join
        Init.create_config(config_path="test/path")
        mock_open.assert_has_calls(
            calls=[
                call("test/path/.heysops.yaml", "w"),
                call().__enter__(),
                call().__enter__().write(CONFIG_TEMPLATE),
                call().__exit__(None, None, None),
            ]
        )

    @patch("libheysops.init.init.os")
    def test_create_config2(self, mock_os):
        mock_os.path.isdir.return_value = False
        mock_os.path.exists.return_value = False
        mock_os.path.join = os.path.join
        self.assertRaises(ValueError, Init.create_config, config_path="test/path")

    @patch("libheysops.init.init.os")
    def test_create_config3(self, mock_os):
        mock_os.path.exists.return_value = True
        mock_os.path.join = os.path.join
        self.assertRaises(FileExistsError, Init.create_config)
