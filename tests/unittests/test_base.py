import os
import subprocess
import unittest
from unittest.mock import patch, MagicMock, call, mock_open

from libheysops.base import BaseAction, SopsNotFoundError


class TestBaseAction(unittest.TestCase):
    @patch("libheysops.base.os")
    def test_find_config1(self, mock_os):
        mock_os.path.exists.return_value = True
        mock_os.path.isfile.return_value = True
        actual = BaseAction.find_config(config_file_path=".heysops.yaml")
        self.assertEqual(".heysops.yaml", actual)

    @patch("libheysops.base.os")
    def test_find_config2(self, mock_os):
        mock_os.path.exists.return_value = False
        mock_os.path.isfile.return_value = False
        mock_os.curdir = os.curdir
        mock_os.path.join = os.path.join
        mock_os.path.abspath = os.path.abspath
        BaseAction._check_folder_for_file = MagicMock(side_effect=[False, False, True])
        actual = BaseAction.find_config(config_file_path=None)
        self.assertEqual(os.path.abspath("../.heysops.yaml"), actual)

    @patch("libheysops.base.os")
    def test_find_config3(self, mock_os):
        mock_os.path.exists.return_value = False
        mock_os.path.isfile.return_value = False
        mock_os.curdir = os.curdir
        mock_os.path.join = os.path.join
        mock_os.path.abspath = os.path.abspath
        mock_os.path.split = os.path.split
        BaseAction._check_folder_for_file = MagicMock(return_value=False)
        self.assertRaises(FileNotFoundError, BaseAction.find_config)

    @patch("libheysops.base.subprocess")
    @patch("libheysops.base.os")
    def test_get_sops1(self, mock_os, mock_subprocess):
        mock_os.path.exists.return_value = True
        mock_os.path.is_file.return_value = True
        actual = BaseAction._get_sops(sops_executable="/path/to/sops")
        self.assertEqual("/path/to/sops", actual)
        mock_subprocess.assert_has_calls(
            calls=[
                call.run(
                    ["/path/to/sops", "-v"],
                    stdout=mock_subprocess.DEVNULL,
                    stderr=mock_subprocess.DEVNULL,
                ),
                call.run().check_returncode(),
            ]
        )

    @patch("libheysops.base.subprocess")
    def test_get_sops2(self, mock_subprocess):
        actual = BaseAction._get_sops()
        self.assertEqual("sops", actual)
        mock_subprocess.assert_has_calls(
            calls=[
                call.run(
                    ["sops", "-v"],
                    stdout=mock_subprocess.DEVNULL,
                    stderr=mock_subprocess.DEVNULL,
                ),
                call.run().check_returncode(),
            ]
        )

    @patch("libheysops.base.subprocess")
    def test_get_sops3(self, mock_subprocess):
        mock_subprocess.run.side_effect = Exception
        self.assertRaises(SopsNotFoundError, BaseAction._get_sops)
        mock_subprocess.assert_has_calls(
            calls=[
                call.run(
                    ["sops", "-v"],
                    stdout=mock_subprocess.DEVNULL,
                    stderr=mock_subprocess.DEVNULL,
                )
            ]
        )

    @patch("libheysops.base.subprocess")
    @patch("libheysops.base.os")
    def test_get_sops4(self, mock_os, mock_subprocess):
        mock_os.path.exists.return_value = True
        mock_os.path.is_file.return_value = True
        mock_subprocess.run.side_effect = Exception
        self.assertRaises(
            SopsNotFoundError, BaseAction._get_sops, sops_executable="some/bad/path"
        )
        mock_subprocess.assert_has_calls(
            calls=[
                call.run(
                    ["some/bad/path", "-v"],
                    stdout=mock_subprocess.DEVNULL,
                    stderr=mock_subprocess.DEVNULL,
                )
            ]
        )

    @patch("libheysops.base.os")
    def test_check_folder_for_file(self, mock_os):
        mock_os.path.exists.return_value = False
        mock_os.path.isdir.return_value = False
        self.assertRaises(
            NotADirectoryError,
            BaseAction._check_folder_for_file,
            folder_path="test",
            filename="path.txt",
        )

        mock_os.path.exists.return_value = True
        mock_os.path.isdir.return_value = True
        mock_os.listdir.return_value = ["path1.txt", "path2.txt"]
        self.assertFalse(
            BaseAction._check_folder_for_file(folder_path="test", filename="path.txt")
        )
        self.assertTrue(
            BaseAction._check_folder_for_file(folder_path="test", filename="path1.txt")
        )

    def test_parse_config(self):
        sample_data = "sample: yaml data"
        with patch("libheysops.base.open", mock_open(read_data=sample_data)) as _:
            actual = BaseAction.parse_config(config_file="something.txt")
            self.assertDictEqual({"sample": "yaml data"}, actual)

    def test_abstract_base_classes(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            self.assertRaises(NotImplementedError, action.run)
            self.assertRaises(
                NotImplementedError, BaseAction.argparse_sub_parser, "test"
            )

    def test_baseaction_init(self):
        with patch.object(BaseAction, "find_config", lambda x, **y: "some/path"):
            with patch.object(
                BaseAction, "parse_config", lambda x, **y: {"config": "data"}
            ):
                with patch.object(
                    BaseAction, "_get_sops", lambda x, **y: "path/to/sops"
                ):
                    action = BaseAction(force=True, config="my/config.file")
                    self.assertTrue(action.force)
                    self.assertEqual("some/path", action.config_path)
                    self.assertDictEqual({"config": "data"}, action.config)
                    self.assertEqual("path/to/sops", action.sops)

    def test_start(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            action.run = MagicMock()
            action.flush_config = MagicMock()
            action.start()

    def test_flush_config(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            with patch("libheysops.base.open", mock_open()) as m:
                action.config = {"sample": {"data": "here"}}
                action.config_path = "if this file exists a test failed.txt"
                action.flush_config()
                m.assert_has_calls(
                    calls=[
                        call("if this file exists a test failed.txt", "w"),
                        call().__enter__(),
                        call().write("sample: {data: here}\n"),
                        call().__exit__(None, None, None),
                    ]
                )

    def test_get_absolute_path(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            action.config_path = "path/to/.heysops.yaml"
            abs_path = action.get_absolute_path(relative_path="new_file")
            self.assertEqual(os.path.abspath("path/to/new_file"), abs_path)

    def test_add_file_to_config1(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            action.config = {
                "secrets": [
                    {
                        "decrypted_path": "path/to/file1.txt",
                        "encrypted_path": "path/to/file1.txt.sops",
                        "type": None,
                    },
                    {
                        "decrypted_path": "path/to/file2.txt",
                        "encrypted_path": "path/to/file2.txt.sops",
                        "type": None,
                    },
                ]
            }
            action.add_file_to_config(
                file_entry={
                    "decrypted_path": "path/to/file3.txt",
                    "encrypted_path": "path/to/file3.txt.sops",
                    "type": None,
                }
            )
            self.assertDictEqual(
                {
                    "secrets": [
                        {
                            "decrypted_path": "path/to/file1.txt",
                            "encrypted_path": "path/to/file1.txt.sops",
                            "type": None,
                        },
                        {
                            "decrypted_path": "path/to/file2.txt",
                            "encrypted_path": "path/to/file2.txt.sops",
                            "type": None,
                        },
                        {
                            "decrypted_path": "path/to/file3.txt",
                            "encrypted_path": "path/to/file3.txt.sops",
                            "type": None,
                        },
                    ]
                },
                action.config,
            )

    def test_add_file_to_config2(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            action.config = {"secrets": []}
            action.add_file_to_config(
                file_entry={
                    "decrypted_path": "path/to/file3.txt",
                    "encrypted_path": "path/to/file3.txt.sops",
                    "type": None,
                }
            )
            self.assertDictEqual(
                {
                    "secrets": [
                        {
                            "decrypted_path": "path/to/file3.txt",
                            "encrypted_path": "path/to/file3.txt.sops",
                            "type": None,
                        }
                    ]
                },
                action.config,
            )

    def test_add_file_to_config3(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            action.config = {
                "secrets": [
                    {
                        "decrypted_path": "path/to/file1.txt",
                        "encrypted_path": "path/to/file1.txt.sops",
                        "type": None,
                    },
                    {
                        "decrypted_path": "path/to/file2.txt",
                        "encrypted_path": "path/to/file2.txt.sops",
                        "type": None,
                    },
                ]
            }
            action.add_file_to_config(
                file_entry={
                    "decrypted_path": "path/to/file2.txt",
                    "encrypted_path": "path/to/file2.a.txt.sops",
                    "type": None,
                }
            )
            self.assertDictEqual(
                {
                    "secrets": [
                        {
                            "decrypted_path": "path/to/file1.txt",
                            "encrypted_path": "path/to/file1.txt.sops",
                            "type": None,
                        },
                        {
                            "decrypted_path": "path/to/file2.txt",
                            "encrypted_path": "path/to/file2.a.txt.sops",
                            "type": None,
                        },
                    ]
                },
                action.config,
            )

    def test_delete_file_from_config(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            action.config = {
                "secrets": [
                    {
                        "decrypted_path": "path/to/file1.txt",
                        "encrypted_path": "path/to/file1.txt.sops",
                        "type": None,
                    },
                    {
                        "decrypted_path": "path/to/file2.txt",
                        "encrypted_path": "path/to/file2.txt.sops",
                        "type": None,
                    },
                ]
            }
            action.delete_file_from_config(file_to_remove="path/to/file2.txt")
            self.assertDictEqual(
                {
                    "secrets": [
                        {
                            "decrypted_path": "path/to/file1.txt",
                            "encrypted_path": "path/to/file1.txt.sops",
                            "type": None,
                        },
                    ]
                },
                action.config,
            )

            action.config = {}
            action.delete_file_from_config(file_to_remove="path/to/file2.txt")
            self.assertDictEqual({}, action.config)

    def test_get_all_decrypted_encrypted_file_paths_from_config(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            action.config = {
                "secrets": [
                    {
                        "decrypted_path": "path/to/file1.txt",
                        "encrypted_path": "path/to/file1.txt.sops",
                        "type": None,
                    },
                    {
                        "decrypted_path": "path/to/file2.txt",
                        "encrypted_path": "path/to/file2.txt.sops",
                        "type": None,
                    },
                ]
            }
            actual_decrypted = action.get_all_decrypted_file_paths_from_config()
            self.assertListEqual(
                ["path/to/file1.txt", "path/to/file2.txt"], actual_decrypted
            )
            actual_encrypted = action.get_all_encrypted_file_paths_from_config()
            self.assertListEqual(
                ["path/to/file1.txt.sops", "path/to/file2.txt.sops"], actual_encrypted
            )

            action.config = {}
            actual_decrypted = action.get_all_decrypted_file_paths_from_config()
            self.assertListEqual([], actual_decrypted)
            actual_encrypted = action.get_all_encrypted_file_paths_from_config()
            self.assertListEqual([], actual_encrypted)

    def test_find_file_in_config(self):
        with patch.object(BaseAction, "__init__", lambda x, **y: None):
            action = BaseAction()
            action.config = {
                "secrets": [
                    {
                        "decrypted_path": "path/to/file1.txt",
                        "encrypted_path": "path/to/file1.txt.sops",
                        "type": None,
                    },
                    {
                        "decrypted_path": "path/to/file2.txt",
                        "encrypted_path": "path/to/file2.txt.sops",
                        "type": None,
                    },
                ]
            }
            actual = action.find_file_in_config(file_path="path/to/file2.txt")
            self.assertDictEqual(
                {
                    "decrypted_path": "path/to/file2.txt",
                    "encrypted_path": "path/to/file2.txt.sops",
                    "type": None,
                },
                actual,
            )
            actual = action.find_file_in_config(file_path="path/to/file3.txt")
            self.assertDictEqual({}, actual)
            action.config = {}
            actual = action.find_file_in_config(file_path="path/to/file3.txt")
            self.assertDictEqual({}, actual)


if __name__ == "__main__":
    unittest.main()
