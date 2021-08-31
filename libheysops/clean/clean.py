import argparse
import logging
import os

from libheysops.base import BaseAction
from libheysops import Action

logger = logging.getLogger()


class Clean(BaseAction):
    def __init__(self, **kwargs):
        super(Clean, self).__init__(**kwargs)

    def run(self, **kwargs) -> None:
        """Entry point for this action's operation

        First encrypts all files tracked by heysops. Then deletes the decrypted file
        associated with each encrypted file.

        Args:
            **kwargs: The keyword arguments from the command line.

        Keyword Args:
            No kwargs are accepted for this action

        Returns:
            None.
        """
        # encrypt all files in the configuration file
        Action.encrypt(FILE="-")

        # remove all decrypted files
        decrypted_file_paths = self.get_all_decrypted_file_paths_from_config()
        for decrypted_file in decrypted_file_paths:
            abs_file = self.get_absolute_path(decrypted_file)
            os.remove(abs_file)
            logger.info("Removed {}".format(decrypted_file))

    @staticmethod
    def argparse_sub_parser(sub_parser) -> argparse.Action:
        """CLI Argument definitions

        Args:
            sub_parser: The sub-command parser object from the main argparse instance.

        Returns:
            argparse.Action: The defined action object.
        """
        return sub_parser.add_parser(
            "clean",
            help="Runs encrypt on all files in the configuration. Then removes all decrypted files.",
        )
