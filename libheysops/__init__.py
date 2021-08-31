__version__ = "0.0.1"


class Action:
    """An interface class, allowing us to easily extend heysops and add new plugins."""

    @staticmethod
    def get_actions() -> dict:
        """Provides a dictionary mapping action command names from argparse to the classes containing
        the logic for the action

        Returns:
            dict: Keys match the argparse sub-parser command name, and the corresponding values are the classes that
              hold the logic for that command.
        """
        # Prevent circular imports
        from .encrypt.encrypt import Encrypt
        from .decrypt.decrypt import Decrypt
        from .forget.forget import Forget
        from .init.init import Init
        from .clean.clean import Clean

        return {
            "init": Init,
            "encrypt": Encrypt,
            "decrypt": Decrypt,
            "clean": Clean,
            "forget": Forget,
        }

    @staticmethod
    def init(**kwargs) -> None:
        """Instantiates the Init class and invokes start() method, passing kwargs to each"""
        from .init.init import Init

        init = Init(**kwargs)
        init.start(**kwargs)

    @staticmethod
    def encrypt(**kwargs):
        """Instantiates the Encrypt class and invokes start() method, passing kwargs to each"""
        from .encrypt.encrypt import Encrypt

        encrypt = Encrypt(**kwargs)
        encrypt.start(**kwargs)

    @staticmethod
    def decrypt(**kwargs):
        """Instantiates the Decrypt class and invokes start() method, passing kwargs to each"""
        from .decrypt.decrypt import Decrypt

        decrypt = Decrypt(**kwargs)
        decrypt.start(**kwargs)

    @staticmethod
    def forget(**kwargs):
        """Instantiates the Forget class and invokes start() method, passing kwargs to each"""
        from .forget.forget import Forget

        forget = Forget(**kwargs)
        forget.start(**kwargs)

    @staticmethod
    def clean(**kwargs):
        """Instantiates the Clean class and invokes start() method, passing kwargs to each"""
        from .clean.clean import Clean

        clean = Clean(**kwargs)
        clean.start(**kwargs)
