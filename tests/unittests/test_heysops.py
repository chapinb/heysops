from unittest import TestCase
from unittest.mock import patch, MagicMock, call

from libheysops import heysops


class TestHeySops(TestCase):
    def test_parse_user_args(self):
        tests = [
            {"desc": "Init command", "args": ["init"], "expected": "init"},
            {"desc": "Encrypt command", "args": ["encrypt"], "expected": "encrypt"},
            {"desc": "Decrypt command", "args": ["decrypt"], "expected": "decrypt"},
            {
                "desc": "Forget command",
                "args": ["forget", "unittesting"],
                "expected": "forget",
            },
            {"desc": "Clean command", "args": ["clean"], "expected": "clean"},
        ]
        for test in tests:
            with self.subTest(msg=test["desc"]):
                parsed_args = heysops.parse_user_args(test["args"])
                self.assertEqual(test["expected"], parsed_args.command)
