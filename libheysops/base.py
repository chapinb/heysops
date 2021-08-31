import argparse
import os
import subprocess
from typing import Union, List

from ruamel.yaml import YAML

CONFIG_TEMPLATE = """---
project:
  # Path to the .gitignore file (including the file name) relative to the location of this configuration file.
  gitignore_path: 

# Within the secrets key we can specify a list of all of the secrets that heysops should assist in managing.
secrets:
  # Example
  # - decrypted_path: some/file/with/api_keys.json
  #   encrypted_path: some/file/with/api_keys.json.sops
  #   type: json


"""


class SopsNotFoundError(Exception):
    def __init__(self, path: Union[str, None] = None):
        if path != "sops" and path is not None:
            message = (
                "Sops not found at {}. Please check your installation "
                "and .heysops.yaml configuration file.".format(path)
            )
        else:
            message = "Sops not found on system path. Please update your environment variable or install sops."

        message += " See https://github.com/mozilla/sops/releases for sops installation packages."
        super().__init__(message)


class BaseAction:
    """The base class for our plugins, providing helper and common methods, defining required structure, and handling
    the boring stuff.

    Args:
        kwargs: Key word arguments from the command line.

    Attributes:
        force: Boolean value for whether overwriting operations should be allowed.
        config_path: The path to a heysops configuration file to load
        config: The loaded heysops configuration file data
        sops: The path to the sops executable

    Environment Variables:
        SOPS_PATH: The path to the sops executable to us. Defaults to the system path.

    Keyword Args:
        force: Boolean value for whether overwriting operations should be allowed.
        config: The path to a heysops configuration file to load


    """

    config_filename_1 = ".heysops.yaml"
    config_filename_2 = ".heysops.yml"

    def __init__(self, **kwargs):
        # Setup common CLI arguments
        self.force = kwargs.get("force", False)

        # Load configuration
        self.config_path = self.find_config(config_file_path=kwargs.get("config"))
        self.config = self.parse_config(config_file=self.config_path)

        # Get sops executable
        self.sops = self._get_sops(sops_executable=os.environ.get("SOPS_PATH"))

    @staticmethod
    def argparse_sub_parser(sub_parser) -> argparse.Action:
        """Required method to supply command line arguments for the action."""
        raise NotImplementedError

    def run(self, **kwargs) -> None:
        """Required method to execute the action."""
        raise NotImplementedError

    def start(self, **kwargs) -> None:
        """Calls the run function, implemented by child classes."""
        self.run(**kwargs)
        self.flush_config()

    @staticmethod
    def parse_config(config_file: str) -> dict:
        """Parse the configuration file.

        Args:
            config_file: Path to the configuration file

        Returns:
            dict: The loaded yaml file
        """
        yaml = YAML(typ="safe")
        with open(config_file, "r") as open_config:
            # noinspection PyyamlLoad
            return yaml.load(open_config)

    def flush_config(self) -> None:
        """Write the configuration data in memory to the configuration file. Overwrites the entire file.

        Returns:
            None
        """
        yaml = YAML(typ="safe")
        with open(self.config_path, "w") as open_config:
            # noinspection PyyamlLoad
            yaml.dump(self.config, open_config)

    @classmethod
    def find_config(cls, config_file_path: Union[str, None] = None) -> str:
        """Looks for a configuration file starting in the current directory and then climbing up the tree.

        If config_file_path is a string value containing a path to a file named ".heysops.yaml" or ".heysops.yml",
        the search is called off and that path is returned.

        Args:
            config_file_path: The path to a provided config file, or None.

        Returns:
            str: Path to a valid ".heysops.yaml" or ".heysops.yml" file.

        """
        if config_file_path is not None and (
            os.path.exists(config_file_path)
            and os.path.isfile(config_file_path)
            and (
                config_file_path.endswith(cls.config_filename_1)
                or config_file_path.endswith(cls.config_filename_2)
            )
        ):
            return config_file_path

        # Check current then parent directories
        folder_to_check = os.curdir
        found = False
        while not found:
            for filename in [cls.config_filename_1, cls.config_filename_2]:
                found = cls._check_folder_for_file(folder_to_check, filename)
                if found:
                    return os.path.join(folder_to_check, filename)

            if not os.path.split(folder_to_check)[1]:
                break  # We are at the root of the drive and didn't find it

            # Set new folder to call
            folder_to_check = os.path.abspath(os.path.join(folder_to_check, ".."))

        raise FileNotFoundError(
            "A configuration file .heysops.yaml or .heysops.yml was not found in this or any parent directories "
            "or your user's home directories. Please run `heysops init` to create one."
        )

    @staticmethod
    def _get_sops(sops_executable: Union[str, None] = None) -> str:
        """Find the sops executable on the path.

        Args:
            sops_executable: A path to the sops binary. If not found, checks for the binary on the path.

        Raises:
             SopsNotFoundError: if it isn't located

        Returns:
            str: Location of the sops binary
        """
        if (
            sops_executable is not None
            and os.path.exists(sops_executable)
            and os.path.isfile(sops_executable)
        ):
            sops = sops_executable
        else:
            sops = "sops"

        try:
            sops_run = subprocess.run(
                [sops, "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            sops_run.check_returncode()
        except Exception:
            raise SopsNotFoundError(path=sops)

        return sops

    @staticmethod
    def _check_folder_for_file(folder_path, filename) -> bool:
        """Check if the file is within the folder. Meant to be called recursively until returning True

        Args:
            folder_path: The directory to search in
            filename: The filename to search for

        Returns:
            bool: Whether or not the filename exists within the folder_path

        Raises:
            NotADirectoryError: if the folder_path is not found or is a file.
        """
        if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
            raise NotADirectoryError(folder_path)

        return filename in os.listdir(folder_path)

    def get_absolute_path(self, relative_path: str) -> str:
        """Render an absolute path using the path to the configuration file and the relative path supplied.

        Args:
            relative_path: The path value, relative to the configuration file it came from.

        Returns:
            str: The absolute path.
        """
        return os.path.join(
            os.path.abspath(os.path.split(self.config_path)[0]), relative_path
        )

    def add_file_to_config(self, file_entry: dict) -> None:
        """Adds a new file to the self.config object's secret array. Flushes data to the configuration file.

        Checks for the existence of the file within the configuration before modifying

        Args:
            file_entry: Dictionary to add to the secrets key, if it isn't found already.

        Returns:
            None
        """
        updated_secrets = []
        file_entry_found = False
        secrets = self.config.get("secrets")
        if not secrets:
            secrets = [{}]
        for entry in secrets:
            if not file_entry_found and (
                file_entry["decrypted_path"] == entry.get("decrypted_path")
                or file_entry["encrypted_path"] == entry.get("encrypted_path")
            ):
                # Update existing record, based on the decrypted path
                updated_secrets.append(file_entry)
                file_entry_found = True
            elif entry:
                # Keep existing records in the list
                updated_secrets.append(entry)

        if not file_entry_found:
            # If we didn't find a record to update, we add a new entry
            updated_secrets.append(file_entry)

        self.config["secrets"] = updated_secrets

    def delete_file_from_config(self, file_to_remove: str) -> None:
        """Removes a file from the self.config object's secret array. Flushes data to the configuration file.

        Args:
            file_to_remove: Either the encrypted or decrypted file path to search for within the config

        Returns:
            None
        """
        updated_secrets = []
        secrets = self.config.get("secrets")
        if not secrets:
            return None  # If there are no secrets, there is nothing to remove
        for entry in secrets:
            if file_to_remove in [
                entry.get("decrypted_path"),
                entry.get("encrypted_path"),
            ]:
                # Skip this entry
                continue
            elif entry:
                # Keep existing records in the list
                updated_secrets.append(entry)

        self.config["secrets"] = updated_secrets

    def get_all_decrypted_file_paths_from_config(self) -> List[str]:
        """Gets all decrypted file paths from the configuration file.

        Returns:
            list: Collection of all decrypted file paths within the heysops configuration file's secrets
        """
        secrets = self.config.get("secrets")
        if not secrets:
            return []
        return [x.get("decrypted_path") for x in secrets]

    def get_all_encrypted_file_paths_from_config(self) -> List[str]:
        """Gets all decrypted file paths from the configuration file.

        Returns:
            list: Collection of all decrypted file paths within the heysops configuration file's secrets
        """
        secrets = self.config.get("secrets")
        if not secrets:
            return []
        return [x.get("encrypted_path") for x in secrets]

    def find_file_in_config(self, file_path: str) -> dict:
        """Finds a specific file from within the configuration. Searches both decrypted and encrypted file names.

        Args:
            file_path: The file path to search

        Returns:
            dict: Returns details about the file if found. Otherwise returns an empty dictionary.
        """
        secrets = self.config.get("secrets")
        if not secrets:
            secrets = [{}]
        for entry in secrets:
            if file_path in [
                entry.get("decrypted_path"),
                entry.get("encrypted_path"),
            ]:
                return entry
        return {}
