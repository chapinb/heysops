import argparse
import logging
import os
import subprocess
from typing import Union

from libheysops.base import BaseAction

logger = logging.getLogger()


class Decrypt(BaseAction):
    def __init__(self, **kwargs):
        super(Decrypt, self).__init__(**kwargs)

    def run(self, **kwargs):
        """Entry point for this action's operation

        Decrypts all files supplied at the command line, or all files found within
        the configuration file.

        Args:
            **kwargs: The keyword arguments from the command line.

        Keyword Args:
           FILE: A list of files to decrypt, or a dash (`-`) character to indicate
             that all files known to heysops (via the configuration file) should
             be decrypted.

        Returns:
            None.
        """
        encrypted_file_paths = kwargs.get("FILE")

        if not encrypted_file_paths or encrypted_file_paths in ["-", ["-"]]:
            encrypted_file_paths = self.get_all_encrypted_file_paths_from_config()

        for encrypted_file_path in encrypted_file_paths:
            config_entry = self.find_file_in_config(file_path=encrypted_file_path)
            # Decrypt the file
            self.decrypt_file(
                file_entry=config_entry.get("encrypted_path"),
                output_type=config_entry.get("type"),
                output_filename=config_entry.get("decrypted_path"),
            )

    def decrypt_file(
        self,
        file_entry: str,
        output_type: Union[str, None] = None,
        output_filename: Union[str, None] = None,
    ) -> None:
        """Perform the decryption operation on a single file.

        Args:
            file_entry: The name and path of the sops encrypted file to decrypt.
            output_type: The output format that sops should use during decryption. If none, sops will pick.
            output_filename: The name and path of the file to write the sops decrypted content to.

        Returns:
            None
        """
        search_entry = self.find_file_in_config(file_entry)

        if not output_filename:
            if search_entry:
                output_filename = search_entry.get("decrypted_path")
            else:
                output_filename = file_entry.replace(".sops", "")

        abs_output_filename = self.get_absolute_path(output_filename)

        if not self.force and os.path.exists(abs_output_filename):
            raise FileExistsError(
                "The output file {} exists and will not be overwritten. "
                "Re-run with `-f` to overwrite.".format(abs_output_filename)
            )

        abs_file_entry = self.get_absolute_path(file_entry)

        if not output_type and search_entry:
            output_type = search_entry.get("type")
        sops_args = [self.sops]
        if output_type:
            sops_args += ["--output-type", output_type]
        sops_args += ["-d", abs_file_entry]

        try:
            logger.debug("Running `{}`".format(" ".join(sops_args)))
            sops_run = subprocess.run(
                sops_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            sops_run.check_returncode()
        except subprocess.CalledProcessError as e:
            message = "Unable to decrypt file. sops command {}. sops error message: {}".format(
                sops_args, e.stderr.decode()
            )
            logger.exception(message, exc_info=e)
            raise OSError(message)

        if len(sops_run.stderr):
            logger.debug(b"sops stderr: " + sops_run.stderr)

        with open(abs_output_filename, "wb") as open_out_file:
            open_out_file.write(sops_run.stdout)

        logger.info(
            "Decrypted file {} at {} as format {}".format(
                file_entry, output_filename, output_type
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
        # Decrypt sub_parser
        cli_decrypt = sub_parser.add_parser(
            "decrypt",
            help="If no files are specified, it looks for a file named .heysops.yaml in the local directory. "
            "If .heysops.yaml is not found in the current directory, it traverses upwards until it finds one. "
            "If it doesn't find one, it warns and exits. Prompts if the decrypted file name already exists.",
        )
        cli_decrypt.add_argument(
            "FILE",
            help="The name of the file to decrypt. If a single dash ('-') or not specified, all files found in "
            ".heysops.yaml are decrypted. You may specify multiple files.",
            nargs="*",
            default="-",
        )
        return cli_decrypt
