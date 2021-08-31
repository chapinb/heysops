import logging
import os
from typing import Union

from libheysops.base import BaseAction, CONFIG_TEMPLATE

logger = logging.getLogger()


class Init(BaseAction):
    def __init__(self, **kwargs):
        # The --config argument overrules the --folder argument
        self.create_config(
            kwargs.get("config") or kwargs.get("folder"), kwargs.get("force")
        )
        super(Init, self).__init__(**kwargs)

    @staticmethod
    def create_config(
        config_path: Union[str, None] = None, force: bool = False
    ) -> None:
        """Create the configuration file in the specified path. Defaults to the current working directory.

        Args:
            config_path: The path to create the configuration file
            force: If True, overwrites existing files

        Returns:
            None
        """
        if (
            config_path
            and not config_path.endswith(BaseAction.config_filename_1)
            and not config_path.endswith(BaseAction.config_filename_2)
        ):
            if os.path.isdir(config_path):
                config_path = os.path.join(config_path, BaseAction.config_filename_1)
            else:
                raise ValueError(
                    "Please provide a path that ends with {} or {}.".format(
                        BaseAction.config_filename_1, BaseAction.config_filename_2
                    )
                )
        else:
            config_path = BaseAction.config_filename_1

        if os.path.exists(config_path) and not force:
            raise FileExistsError(
                "The configuration file {} exists. "
                "Please remove it or use `-f` to overwrite it.".format(config_path)
            )

        logger.debug("Creating configuration file {}".format(config_path))
        with open(config_path, "w") as config_file:
            config_file.write(CONFIG_TEMPLATE)

        logger.info("Created {}".format(config_path))

    def run(self, **kwargs) -> None:
        """Obligated function, but we must perform the init work prior to calling super() due to config checking."""
        return None  # pragma: no cover

    @staticmethod
    def argparse_sub_parser(sub_parser):
        """CLI Argument definitions

        Args:
            sub_parser: The sub-command parser object from the main argparse instance.

        Returns:
            argparse.Action: The defined action object.
        """
        # Init sub_parser
        cli_init = sub_parser.add_parser(
            "init",
            help="Creates the .heysops.yaml file in the current directory. If `-c` or `--config` is specified, "
            "it will create the .heysops.yaml at that path. Please be sure that the specified path uses the "
            "file name .heysops.yaml.",
        )
        cli_init.add_argument(
            "--folder",
            help="The name of the folder to place a .heysops.yaml file.",
            default=os.path.abspath(os.curdir),
        )
        return cli_init
