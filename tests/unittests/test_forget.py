import unittest
from unittest.mock import patch, MagicMock

from libheysops.forget.forget import Forget


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        with patch.object(Forget, "__init__", lambda x, **y: None):
            self.action = Forget()

    def test_run(self):
        self.action.find_file_in_config = MagicMock(return_value={})
        self.action.delete_file_from_config = MagicMock()

        self.action.run(FILE=["test123.txt"])
        self.action.find_file_in_config.assert_called_once_with(file_path="test123.txt")
        self.action.delete_file_from_config.assert_not_called()

        self.action.find_file_in_config = MagicMock(
            return_value={
                "decrypted_path": "test123.txt",
                "encrypted_path": "test213.txt.sops",
                "type": None,
            }
        )
        self.action.run(FILE=["test123.txt"])
        self.action.delete_file_from_config.assert_called_once_with(
            file_to_remove="test213.txt.sops"
        )


if __name__ == "__main__":
    unittest.main()
