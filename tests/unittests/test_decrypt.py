import unittest
from unittest.mock import patch, MagicMock, call, mock_open

from libheysops.decrypt.decrypt import Decrypt


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        with patch.object(Decrypt, "__init__", lambda x, **y: None):
            self.action = Decrypt()

    def test_run1(self):
        self.action.find_file_in_config = MagicMock(
            return_value={
                "encrypted_path": "test.txt.sops",
                "decrypted_path": "test.txt",
                "type": None,
            }
        )
        self.action.decrypt_file = MagicMock()

        self.action.run(FILE=["test123.txt"])
        self.action.find_file_in_config.assert_called_once_with(file_path="test123.txt")
        self.action.decrypt_file.assert_called_once_with(
            file_entry="test.txt.sops",
            output_type=None,
            output_filename="test.txt",
        )

    def test_run2(self):
        self.action.find_file_in_config = MagicMock(
            return_value={
                "encrypted_path": "test.txt.sops",
                "decrypted_path": "test.txt",
                "type": None,
            }
        )
        self.action.decrypt_file = MagicMock()

        self.action.get_all_encrypted_file_paths_from_config = MagicMock(
            return_value=["test456.txt"]
        )
        self.action.find_file_in_config.reset_mock()
        self.action.decrypt_file.reset_mock()
        self.action.run(FILE="-")
        self.action.find_file_in_config.assert_called_once_with(file_path="test456.txt")
        self.action.decrypt_file.assert_called_once_with(
            file_entry="test.txt.sops",
            output_type=None,
            output_filename="test.txt",
        )

    @patch("libheysops.decrypt.decrypt.subprocess")
    def test_decrypt_file1(self, mock_subprocess):
        self.action.find_file_in_config = MagicMock(
            return_value={
                "encrypted_path": "test.txt.sops",
                "decrypted_path": "test.txt",
                "type": None,
            }
        )
        self.action.get_absolute_path = MagicMock(
            side_effect=lambda x: "a/{}".format(x)
        )
        self.action.sops = "sops"
        self.action.force = False
        mock_run = MagicMock()
        mock_run.stderr = b""
        mock_run.stdout = b"data"
        mock_subprocess.run.return_value = mock_run
        with patch("libheysops.decrypt.decrypt.open", mock_open()) as m:
            self.action.decrypt_file(
                file_entry="test.txt.sops", output_type=None, output_filename="test.txt"
            )
            mock_subprocess.assert_has_calls(
                calls=[
                    call.run(
                        ["sops", "-d", "a/test.txt.sops"],
                        stdout=mock_subprocess.PIPE,
                        stderr=mock_subprocess.PIPE,
                    )
                ]
            )
            m.assert_has_calls(
                calls=[
                    call("a/test.txt", "wb"),
                    call().__enter__(),
                    call().write(b"data"),
                    call().__exit__(None, None, None),
                ]
            )

    @patch("libheysops.decrypt.decrypt.subprocess")
    def test_decrypt_file2(self, mock_subprocess):
        self.action.find_file_in_config = MagicMock(
            return_value={
                "encrypted_path": "test.txt.sops",
                "decrypted_path": "test.txt",
                "type": None,
            }
        )
        self.action.get_absolute_path = MagicMock(
            side_effect=lambda x: "a/{}".format(x)
        )
        self.action.sops = "sops"
        self.action.force = False
        mock_run = MagicMock()
        mock_run.stderr = b"err"
        mock_run.stdout = b"data"
        mock_subprocess.run.return_value = mock_run
        with patch("libheysops.decrypt.decrypt.open", mock_open()) as m:
            self.action.decrypt_file(file_entry="test.txt.sops", output_type="binary")
            mock_subprocess.assert_has_calls(
                calls=[
                    call.run(
                        ["sops", "--output-type", "binary", "-d", "a/test.txt.sops"],
                        stdout=mock_subprocess.PIPE,
                        stderr=mock_subprocess.PIPE,
                    )
                ]
            )
            m.assert_has_calls(
                calls=[
                    call("a/test.txt", "wb"),
                    call().__enter__(),
                    call().write(b"data"),
                    call().__exit__(None, None, None),
                ]
            )

    @patch("libheysops.decrypt.decrypt.subprocess")
    def test_decrypt_file3(self, mock_subprocess):
        self.action.find_file_in_config = MagicMock(return_value={})
        self.action.get_absolute_path = MagicMock(
            side_effect=lambda x: "a/{}".format(x)
        )
        self.action.sops = "sops"
        self.action.force = False
        mock_run = MagicMock()
        mock_run.stderr = b"err"
        mock_run.stdout = b"data"
        mock_subprocess.run.return_value = mock_run
        with patch("libheysops.decrypt.decrypt.open", mock_open()) as m:
            self.action.decrypt_file(file_entry="test.txt.sops", output_type="binary")
            mock_subprocess.assert_has_calls(
                calls=[
                    call.run(
                        ["sops", "--output-type", "binary", "-d", "a/test.txt.sops"],
                        stdout=mock_subprocess.PIPE,
                        stderr=mock_subprocess.PIPE,
                    )
                ]
            )
            m.assert_has_calls(
                calls=[
                    call("a/test.txt", "wb"),
                    call().__enter__(),
                    call().write(b"data"),
                    call().__exit__(None, None, None),
                ]
            )


if __name__ == "__main__":
    unittest.main()
