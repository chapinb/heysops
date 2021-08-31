import argparse
import logging
import sys
from typing import Union, List

from libheysops import Action, __version__

logger = logging.getLogger()


def setup_logging(
    logging_obj: logging.Logger, log_file: Union[str, None] = None, verbose: int = 0
) -> None:
    """Function to setup logging configuration and test it.

    Args:
        logging_obj: A logging instance, returned from logging.getLogger().
        log_file: File path to write log messages to.
        verbose: 0 for warning in stderr, 1 for info, 2 for debug.

    Examples:
        >>> sample_logger = logging.getLogger(name=__name__)
        >>> log_path = "sample.log"
        >>> setup_logging(sample_logger, log_path, verbose=True)
        >>> sample_logger.debug("This is a debug message")
        >>> sample_logger.info("This is an info message")
        >>> sample_logger.warning("This is a warning message")
        >>> sample_logger.error("This is a error message")
        >>> sample_logger.critical("This is a critical message")
    """
    logging_obj.setLevel(logging.INFO)

    log_format = logging.Formatter(
        "%(asctime)s %(filename)s %(levelname)s %(module)s "
        "%(funcName)s %(lineno)d %(message)s"
    )

    # Setup STDERR logging, allowing you uninterrupted
    # STDOUT redirection
    stderr_handle = logging.StreamHandler(stream=sys.stderr)
    if verbose == 2:
        stderr_handle.setLevel(logging.DEBUG)
    elif verbose == 1:
        stderr_handle.setLevel(logging.INFO)
    else:
        stderr_handle.setLevel(logging.WARNING)
    stderr_handle.setFormatter(log_format)
    logging_obj.addHandler(stderr_handle)

    # Setup file logging
    if log_file:
        file_handle = logging.FileHandler(log_file, "a")
        file_handle.setLevel(logging.INFO)
        file_handle.setFormatter(log_format)
        logging_obj.addHandler(file_handle)


def parse_user_args(user_args: Union[List, None] = None) -> argparse.Namespace:
    """Parse user supplied command line arguments using the configuration below and defined within each
    plugin's argparse definition.

    Args:
        user_args: A list of arguments supplied at the command line.

    Returns:
        argparse.Namespace: Namespace mapping the arguments in a manner that eases reference during execution.
    """
    if not user_args:  # pragma: no cover
        user_args = sys.argv[1:]

    cli_args = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        epilog="Developed by Chapin Bryce, v{}, MIT License".format(__version__),
    )
    sub_parser = cli_args.add_subparsers(
        title="command", required=False, dest="command"
    )
    cli_args.add_argument(
        "-c", "--config", help="Path to a .heysops.yaml configuration file."
    )
    cli_args.add_argument("-f", "--force", help="Force an action.", action="store_true")
    cli_args.add_argument("-l", "--log", help="Path to a log file to write to.")
    cli_args.add_argument(
        "-v",
        "--verbose",
        help="Print informational messages. Call twice to print debug messages.",
        action="count",
        default=0,
    )
    cli_args.add_argument(
        "-V",
        "--version",
        help="Print version information and exit",
        action="version",
        version="%(prog)s {}".format(__version__),
    )

    for action_name, action_class in Action.get_actions().items():
        new_parser = action_class.argparse_sub_parser(sub_parser=sub_parser)
        new_parser.set_defaults(func=getattr(Action, action_name))

    return cli_args.parse_args(user_args)


def main(user_args: Union[List, None] = None) -> None:
    """The primary controller and entrypoint.

    Args:
        user_args: A list of command line arguments to parse.

    Returns:
        None
    """
    parsed_args = parse_user_args(user_args=user_args)

    setup_logging(logger, parsed_args.log, parsed_args.verbose)

    logger.debug("The following arguments were provided")
    for i, j in vars(parsed_args).items():
        logger.debug("{}: {}".format(i, j))

    # Invoke the command's function, passing all arguments as keyword arguments.
    logger.debug("Calling command {}".format(parsed_args.command))
    parsed_args.func(**vars(parsed_args))


if __name__ == "__main__":
    main()
