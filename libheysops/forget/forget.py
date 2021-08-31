import argparse
import logging

from libheysops.base import BaseAction

logger = logging.getLogger()


class Forget(BaseAction):
    def __init__(self, **kwargs):
        super(Forget, self).__init__(**kwargs)

    def run(self, **kwargs) -> None:
        """Entry point for this action's operation

        Encrypts all files supplied at the command line, or all files found within
        the configuration file.

        Args:
            **kwargs: The keyword arguments from the command line.

        Keyword Args:
           FILE: A list of files to remove from the heysops configuration file.

        Returns:
            None.
        """
        file_paths = kwargs.get("FILE", [])

        for file_path in file_paths:
            config_entry = self.find_file_in_config(file_path=file_path)
            if not config_entry:
                logger.warning(
                    "{} not found in configuration. No action taken.".format(file_path)
                )
                continue

            self.delete_file_from_config(
                file_to_remove=config_entry.get("encrypted_path")
            )
            logger.info(
                "{} removed from the configuration file.".format(
                    config_entry.get("encrypted_file")
                )
            )

    @staticmethod
    def argparse_sub_parser(sub_parser) -> argparse.Action:
        """CLI Argument definitions

        Args:
            sub_parser: The sub-command parser object from the main argparse instance.

        Returns:
            argparse.Action: The defined action object.
        """
        cli_forget = sub_parser.add_parser(
            "forget",
            help="Remove a file from the .heysops.yaml. This will leave the file on the system and no "
            "longer interact with it through other commands.",
        )
        cli_forget.add_argument(
            "FILE",
            help="The name of the encrypted or decrypted file to forget. You may specify multiple files.",
            nargs="+",
        )
        return cli_forget
