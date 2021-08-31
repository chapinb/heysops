import argparse
import logging
import os
import subprocess
from typing import Dict, Union

from libheysops.base import BaseAction

logger = logging.getLogger()


class Encrypt(BaseAction):
    def __init__(self, **kwargs):
        super(Encrypt, self).__init__(**kwargs)

    def run(self, **kwargs):
        """Entry point for this action's operation

        Encrypts all files supplied at the command line, or all files found within
        the configuration file.

        Args:
            **kwargs: The keyword arguments from the command line.

        Keyword Args:
            FILE: A list of files to decrypt, or a dash (`-`) character to indicate
              that all files known to heysops (via the configuration file) should
              be decrypted.
            type: The type value to pass along to sops
            output: The file name to use when writing the encrypted file

        Returns:
            None.
        """
        decrypted_file_paths = kwargs.get("FILE")

        if not decrypted_file_paths or decrypted_file_paths in ["-", ["-"]]:
            decrypted_file_paths = self.get_all_decrypted_file_paths_from_config()

        for decrypted_file_path in decrypted_file_paths:
            prior_config = self.find_file_in_config(file_path=decrypted_file_path)
            # Encrypt the file
            encrypted_information = self.encrypt_file(
                file_entry=decrypted_file_path,
                input_type=kwargs.get("type"),
                output_filename=kwargs.get("output"),
            )

            if encrypted_information:
                self.add_file_to_config(encrypted_information)
                self.add_file_to_gitignore(
                    encrypted_information,
                    prior_decrypted_file=prior_config.get("decrypted_path"),
                )

    def encrypt_file(
        self,
        file_entry: str,
        input_type: Union[str, None] = None,
        output_filename: Union[str, None] = None,
    ) -> Dict[str, str]:
        """Performs the encryption operation on a single file.

        Args:
            file_entry: The name and path of the file to encrypt with sops.
            input_type: The output format that sops should use during encryption. If none, sops will pick.
            output_filename: The name and path of the file to write the sops encrypted content to.

        Returns:
            dict: Key value pairs that mimic the data structure for a single secrets entry in the heysops config.
        """
        search_entry = self.find_file_in_config(file_entry)

        if not output_filename:
            if search_entry:
                output_filename = search_entry.get("encrypted_path")
            else:
                output_filename = "{}.sops".format(file_entry)
        if not input_type and search_entry:
            input_type = search_entry.get("type")
        sops_args = [self.sops]
        if input_type:
            sops_args += ["--input-type", input_type]

        abs_file_entry = self.get_absolute_path(file_entry)
        sops_args += ["-e", abs_file_entry]

        if not os.path.exists(abs_file_entry):
            logger.warning("File {} no longer present. Removing from configuration.")
            self.delete_file_from_config(file_to_remove=abs_file_entry)
            return {}

        try:
            logger.debug("Running `{}`".format(" ".join(sops_args)))
            sops_run = subprocess.run(
                sops_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            sops_run.check_returncode()
        except subprocess.CalledProcessError as e:
            message = "Unable to encrypt file. sops command {}. sops error message: {}".format(
                sops_args, e.stderr.decode()
            )
            logger.exception(message, exc_info=e)
            raise OSError(message)

        if len(sops_run.stderr):
            logger.debug(b"sops stderr: " + sops_run.stderr)

        abs_output_filename = self.get_absolute_path(output_filename)

        with open(abs_output_filename, "wb") as open_out_file:
            open_out_file.write(sops_run.stdout)

        logger.info(
            "Encrypted file {} at {} as format {}".format(
                file_entry, output_filename, input_type
            )
        )

        return {
            "decrypted_path": file_entry,
            "encrypted_path": output_filename,
            "type": input_type,
        }

    def add_file_to_gitignore(
        self, file_entry: dict, prior_decrypted_file: Union[str, None] = None
    ) -> None:
        """Adds the file to .gitignore if it isn't already present. Tries to preserve existing order and structure of
        the file.

        Args:
            file_entry: The dictionary object returned by Encrypt.encrypt_file containing keys for
              "decrypted_path", "encrypted_path", and "type". Uses "decrypted_path" to ensure that
              the sensitive content is not accidentally added to git.
            prior_decrypted_file: The name of a previous entry when the decrypted_path changes.

        Returns:
            None
        """
        gitignore_path = self.config.get("project", {}).get("gitignore_path")
        if not self.config.get("project", {}).get("gitignore_path"):
            try:
                gitignore_path = self.find_gitignore_file()
            except FileNotFoundError:
                logger.warning(
                    ".gitignore file not found. Creating one alongside {}".format(
                        self.config_path
                    )
                )
                gitignore_path = os.path.join(
                    os.path.split(self.config_path)[0], ".gitignore"
                )

            # Update the config to use this path
            if "project" not in self.config:
                self.config["project"] = {}
            self.config["project"]["gitignore_path"] = gitignore_path
            self.flush_config()

        with open(gitignore_path, "r") as open_gitignore:
            new_gitignore_lines = []
            found_file = False
            for raw_line in open_gitignore:
                line = raw_line.strip()
                if line != prior_decrypted_file:
                    # Remove any lines that match the prior file name
                    new_gitignore_lines.append(line + os.linesep)
                if line == file_entry.get("decrypted_path"):
                    found_file = True

        if not found_file:
            # Add new decrypted path to gitignore
            new_gitignore_lines.append(file_entry["decrypted_path"] + os.linesep)

        with open(gitignore_path, "w") as open_gitignore:
            open_gitignore.writelines(new_gitignore_lines)

    def find_gitignore_file(self) -> str:
        """Search for a .gitignore file.

        Raises:
            FileNotFoundError: If a .gitignore file is not identified

        Returns:
            str: Path to a discovered .gitignore file.
        """
        # Find the gitignore file
        folder_to_check = os.curdir
        filename = ".gitignore"
        found = False
        while not found:
            found = self._check_folder_for_file(folder_to_check, filename)
            if found:
                return os.path.join(folder_to_check, filename)

            if not os.path.split(folder_to_check)[1]:
                break  # We are at the root of the drive and didn't find it

            # Set new folder to call
            folder_to_check = os.path.abspath(os.path.join(folder_to_check, ".."))

        raise FileNotFoundError("Could not find a .gitignore file.")

    @staticmethod
    def argparse_sub_parser(sub_parser) -> argparse.Action:
        """CLI Argument definitions

        Args:
            sub_parser: The sub-command parser object from the main argparse instance.

        Returns:
            argparse.Action: The defined action object.
        """
        # Encrypt sub_parser
        cli_encrypt = sub_parser.add_parser(
            "encrypt",
            help="Encrypts all files that were previously encrypted with this tool. Uses the .heysops.yaml file "
            "in the local directory. If .heysops.yaml is not found in the current directory, it traverses "
            "upwards until it finds one. If it doesn't find one, it warns and exits.",
        )
        cli_encrypt.add_argument(
            "-t",
            "--type",
            help="The --input-type to pass to sops when encrypting. Otherwise the extension will inform sops' "
            "encryption process. Will use the same type on decryption, or whatever value is stored within "
            ".heysops.yaml",
            choices=["json", "yaml", "dotenv", "binary"],
        )
        cli_encrypt.add_argument(
            "-o",
            "--output",
            help="A custom filename to write the encrypted data to. Saved within your .heysops.yaml configuration "
            "file. Not available if you do not specify a single file name",
        )
        cli_encrypt.add_argument(
            "FILE",
            help="The name of the file to encrypt. If a single dash ('-') or not specified, all files found in "
            ".heysops.yaml are encrypted. You may specify multiple files.",
            nargs="*",
            default="-",
        )
        return cli_encrypt
