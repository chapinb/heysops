import os
import unittest
from unittest.mock import patch, MagicMock, call, mock_open

from libheysops.encrypt.encrypt import Encrypt


class MyTestCase(unittest.TestCase):
    def setUp(self) -> None:
        with patch.object(Encrypt, "__init__", lambda x, **y: None):
            self.action = Encrypt()

    def test_run1(self):
        self.action.find_file_in_config = MagicMock(
            return_value={
                "encrypted_path": "test.txt.sops",
                "decrypted_path": "test.txt",
                "type": None,
            }
        )
        self.action.encrypt_file = MagicMock(
            return_value={
                "decrypted_path": "test.txt",
                "encrypted_path": "test.txt.sops",
                "type": None,
            }
        )
        self.action.add_file_to_config = MagicMock()
        self.action.add_file_to_gitignore = MagicMock()

        self.action.run(FILE=["test123.txt"])
        self.action.find_file_in_config.assert_called_once_with(file_path="test123.txt")
        self.action.encrypt_file.assert_called_once_with(
            file_entry="test123.txt",
            input_type=None,
            output_filename=None,
        )
        self.action.add_file_to_config.assert_called_once_with(
            {
                "decrypted_path": "test.txt",
                "encrypted_path": "test.txt.sops",
                "type": None,
            }
        )
        self.action.add_file_to_gitignore.assert_called_once_with(
            {
                "decrypted_path": "test.txt",
                "encrypted_path": "test.txt.sops",
                "type": None,
            },
            prior_decrypted_file="test.txt",
        )

        self.action.get_all_decrypted_file_paths_from_config = MagicMock(
            return_value=[]
        )
        self.action.run(FILE="-")

    @patch("libheysops.encrypt.encrypt.subprocess")
    @patch("libheysops.encrypt.encrypt.os")
    def test_encrypt_file1(self, mock_os, mock_subprocess):
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
        mock_os.path.exists.return_value = True
        mock_run = MagicMock()
        mock_run.stderr = b""
        mock_run.stdout = b"data"
        mock_subprocess.run.return_value = mock_run
        with patch("libheysops.encrypt.encrypt.open", mock_open()) as m:
            self.action.encrypt_file(
                file_entry="test.txt", input_type=None, output_filename="test.txt.sops"
            )
            mock_subprocess.assert_has_calls(
                calls=[
                    call.run(
                        ["sops", "-e", "a/test.txt"],
                        stdout=mock_subprocess.PIPE,
                        stderr=mock_subprocess.PIPE,
                    )
                ]
            )
            m.assert_has_calls(
                calls=[
                    call("a/test.txt.sops", "wb"),
                    call().__enter__(),
                    call().write(b"data"),
                    call().__exit__(None, None, None),
                ]
            )

    @patch("libheysops.encrypt.encrypt.subprocess")
    @patch("libheysops.encrypt.encrypt.os")
    def test_encrypt_file2(self, mock_os, mock_subprocess):
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
        mock_os.path.exists.return_value = True
        mock_run = MagicMock()
        mock_run.stderr = b"err"
        mock_run.stdout = b"data"
        mock_subprocess.run.return_value = mock_run
        with patch("libheysops.encrypt.encrypt.open", mock_open()) as m:
            self.action.encrypt_file(file_entry="test.txt", input_type="binary")
            mock_subprocess.assert_has_calls(
                calls=[
                    call.run(
                        ["sops", "--input-type", "binary", "-e", "a/test.txt"],
                        stdout=mock_subprocess.PIPE,
                        stderr=mock_subprocess.PIPE,
                    )
                ]
            )
            m.assert_has_calls(
                calls=[
                    call("a/test.txt.sops", "wb"),
                    call().__enter__(),
                    call().write(b"data"),
                    call().__exit__(None, None, None),
                ]
            )

    @patch("libheysops.encrypt.encrypt.subprocess")
    @patch("libheysops.encrypt.encrypt.os")
    def test_decrypt_file3(self, mock_os, mock_subprocess):
        self.action.find_file_in_config = MagicMock(return_value={})
        self.action.get_absolute_path = MagicMock(
            side_effect=lambda x: "a/{}".format(x)
        )
        self.action.sops = "sops"
        self.action.force = False
        mock_os.path.exists.return_value = True
        mock_run = MagicMock()
        mock_run.stderr = b"err"
        mock_run.stdout = b"data"
        mock_subprocess.run.return_value = mock_run
        with patch("libheysops.encrypt.encrypt.open", mock_open()) as m:
            self.action.encrypt_file(file_entry="test.txt", input_type="binary")
            mock_subprocess.assert_has_calls(
                calls=[
                    call.run(
                        ["sops", "--input-type", "binary", "-e", "a/test.txt"],
                        stdout=mock_subprocess.PIPE,
                        stderr=mock_subprocess.PIPE,
                    )
                ]
            )
            m.assert_has_calls(
                calls=[
                    call("a/test.txt.sops", "wb"),
                    call().__enter__(),
                    call().write(b"data"),
                    call().__exit__(None, None, None),
                ]
            )

    def test_decrypt_file4(self):
        self.action.find_file_in_config = MagicMock(return_value={})
        self.action.get_absolute_path = MagicMock(
            side_effect=lambda x: "a/{}".format(x)
        )
        self.action.sops = "sops"
        self.action.force = False
        self.action.delete_file_from_config = MagicMock()
        self.action.encrypt_file(file_entry="test.txt", input_type="binary")
        self.action.delete_file_from_config.assert_called_once_with(
            file_to_remove="a/test.txt"
        )

    def test_find_gitignore_files(self):
        self.action._check_folder_for_file = MagicMock(
            side_effect=[False, False, False, True]
        )
        actual = self.action.find_gitignore_file()
        self.assertEqual(
            os.path.abspath(os.path.join(os.curdir, "../../../.gitignore")), actual
        )

        # Cause the search to go to the root of the drive
        self.action._check_folder_for_file = MagicMock(return_value=False)
        self.assertRaises(FileNotFoundError, self.action.find_gitignore_file)

    def test_add_file_to_gitignore1(self):
        sample_content = ["testfile.txt", "# Commented entry", "", "Skip a line"]
        sample_gitignore = os.linesep.join(sample_content)
        expected_content = sample_content
        expected_content.append("test.txt")
        with patch(
            "libheysops.encrypt.encrypt.open", mock_open(read_data=sample_gitignore)
        ) as m:
            self.action.config = {}
            self.action.find_gitignore_file = MagicMock(
                return_value="not_a_real_filename.txt"
            )
            self.action.flush_config = MagicMock()
            self.action.add_file_to_gitignore(
                {
                    "decrypted_path": "test.txt",
                    "encrypted_path": "test.txt.sops",
                    "type": None,
                }
            )
            self.action.find_gitignore_file.assert_called_once()
            self.action.flush_config.assert_called_once()
            self.assertEqual(
                "not_a_real_filename.txt",
                self.action.config.get("project", {}).get("gitignore_path"),
            )
            m.assert_has_calls(
                calls=[
                    call("not_a_real_filename.txt", "r"),
                    call().__enter__(),
                    call().__iter__(),
                    call().__exit__(None, None, None),
                    call("not_a_real_filename.txt", "w"),
                    call().__enter__(),
                    call().writelines([x + os.linesep for x in expected_content]),
                    call().__exit__(None, None, None),
                ]
            )

    def test_add_file_to_gitignore2(self):
        sample_content = ["testfile.txt", "# Commented entry", "", "Skip a line"]
        sample_gitignore = os.linesep.join(sample_content)
        with patch(
            "libheysops.encrypt.encrypt.open", mock_open(read_data=sample_gitignore)
        ) as m:
            self.action.config = {}
            self.action.find_gitignore_file = MagicMock(
                return_value="not_a_real_filename.txt"
            )
            self.action.flush_config = MagicMock()
            self.action.add_file_to_gitignore(
                {
                    "decrypted_path": "testfile.txt",
                    "encrypted_path": "testfile.txt.sops",
                    "type": None,
                }
            )
            self.action.find_gitignore_file.assert_called_once()
            self.action.flush_config.assert_called_once()
            self.assertEqual(
                "not_a_real_filename.txt",
                self.action.config.get("project", {}).get("gitignore_path"),
            )
            m.assert_has_calls(
                calls=[
                    call("not_a_real_filename.txt", "r"),
                    call().__enter__(),
                    call().__iter__(),
                    call().__exit__(None, None, None),
                    call("not_a_real_filename.txt", "w"),
                    call().__enter__(),
                    call().writelines([x + os.linesep for x in sample_content]),
                    call().__exit__(None, None, None),
                ]
            )


if __name__ == "__main__":
    unittest.main()
