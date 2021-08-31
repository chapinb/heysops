import unittest
from unittest.mock import patch, MagicMock, call

from libheysops.clean.clean import Clean


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        with patch.object(Clean, "__init__", lambda x, **y: None):
            self.action = Clean()

    def test_run(self):
        self.action.get_all_decrypted_file_paths_from_config = MagicMock(
            return_value=["a.txt", "b.txt"]
        )
        self.action.get_absolute_path = MagicMock(
            side_effect=lambda x: "a/{}".format(x)
        )

        with patch("libheysops.clean.clean.Action") as mock_action:
            with patch("libheysops.clean.clean.os") as mock_os:
                self.action.run()
                mock_os.remove.assert_has_calls(
                    calls=[
                        call("a/a.txt"),
                        call("a/b.txt"),
                    ]
                )
                mock_action.encrypt.assert_called_once_with(FILE="-")


if __name__ == "__main__":
    unittest.main()
