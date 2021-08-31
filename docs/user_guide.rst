User Guide
=================

Installation
----------------------

You must have the following before starting installation:

* Python 3.6+
* Sops
* A .sops.yaml file configured with keys to encrypt/decrypt your data

Once the above dependencies are met, you can install heysops by running ``pip install heysops``. This will
pull the latest version from PyPI and install the heysops tool and supporting modules.

Usage
--------------

The best place to start is by running ``heysops --help`` and viewing the command line documentation.

.. code-block:: text

   heysops --help
   usage: heysops [-h] [-c CONFIG] [-f] [-l LOG] [-v] [-V] {init,encrypt,decrypt,clean,forget} ...

   optional arguments:
     -h, --help            show this help message and exit
     -c CONFIG, --config CONFIG
                           Path to a .heysops.yaml configuration file. (default: None)
     -f, --force           Force an action. (default: False)
     -l LOG, --log LOG     Path to a log file to write to. (default: None)
     -v, --verbose         Print informational messages. Call twice to print debug messages. (default: 0)
     -V, --version         Print version information and exit

   command:
     {init,encrypt,decrypt,clean,forget}
       init                Creates the .heysops.yaml file in the current directory. If `-c` or `--config` is specified, it will create the .heysops.yaml at that path. Please be
                           sure that the specified path uses the file name .heysops.yaml.
       encrypt             Encrypts all files that were previously encrypted with this tool. Uses the .heysops.yaml file in the local directory. If .heysops.yaml is not found in
                           the current directory, it traverses upwards until it finds one. If it doesn't find one, it warns and exits.
       decrypt             If no files are specified, it looks for a file named .heysops.yaml in the local directory. If .heysops.yaml is not found in the current directory, it
                           traverses upwards until it finds one. If it doesn't find one, it warns and exits. Prompts if the decrypted file name already exists.
       clean               Runs encrypt on all files in the configuration. Then removes all decrypted files.
       forget              Remove a file from the .heysops.yaml. This will leave the file on the system and no longer interact with it through other commands.

   Developed by Chapin Bryce, v0.0.1, MIT License

Init
+++++++++

The init command is intended to run at the initial usage of heysops. It creates the .heysops.yaml file with template
data. You can modify the generated template directly or as you use the tool it will update the configuration file
for you.

Help information:

.. code-block:: text

   heysops init --help
   usage: heysops init [-h] [--folder FOLDER]

   optional arguments:
     -h, --help       show this help message and exit
     --folder FOLDER  The name of the folder to place a .heysops.yaml file.


Usage Examples:

:``heysops init``: Creates the .heysops.yaml file in the current directory

:``heysops init --folder my-project-folder/``: Specifying a folder name to write the configuration file.

Encrypt
++++++++++

The encrypt command will encrypt the specified files, or all files if none are specified. If the file is not known in
the configuration file, it will add to the configuration file. You can use the ``--type`` argument to control the
data type that sops should use (as the ``--input-type`` argument to sops). Additionally the ``--output`` argument
allows the specification of a path to write the encrypted content.

Help information:

.. code-block:: text

   heysops encrypt --help
   usage: heysops encrypt [-h] [-t {json,yaml,dotenv,binary}] [-o OUTPUT] [FILE ...]

   positional arguments:
     FILE                  The name of the file to encrypt. If a single dash ('-') or not specified, all files found in .heysops.yaml are encrypted. You may specify multiple
                           files.

   optional arguments:
     -h, --help            show this help message and exit
     -t {json,yaml,dotenv,binary}, --type {json,yaml,dotenv,binary}
                           The --input-type to pass to sops when encrypting. Otherwise the extension will inform sops' encryption process. Will use the same type on decryption,
                           or whatever value is stored within .heysops.yaml
     -o OUTPUT, --output OUTPUT
                           A custom filename to write the encrypted data to. Saved within your .heysops.yaml configuration file. Not available if you do not specify a single file
                           name

Usage examples:

:``heysops encrypt db_creds.json``: This will read "db_creds.json" and store the encrypted content in a
    file named "db_creds.json.sops". It will then add an entry to the .gitignore file for "db_creds.json" and then
    update the heysops configuration file (".heysops.yaml").


:``heysops encrypt db_creds.json -t json -o auth/db_creds.json.sops``: This will read "db_creds.json" and
    store the encrypted content in a file named "auth/db_creds.json.sops".
    It will then add an entry to the .gitignore file for "db_creds.json" and then
    update the heysops configuration file (".heysops.yaml").

:``heysops encrypt``: This will read the heysops configuration file and
    encrypt all files specified. It will use the "decryption_path" stored inside the configuration file to determine
    what paths to write the decrypted data to. It will also use the "type" stored inside the configuration file to
    determine the "--output-type" to supply to sops. Useful to run before checking into git.

Decrypt
+++++++++

This command decrypts the specified files, or all files found in the configuration file if none are found.

Help information:

.. code-block::

   heysops decrypt --help
   usage: heysops decrypt [-h] [FILE ...]

   positional arguments:
     FILE        The name of the file to decrypt. If a single dash ('-') or not specified, all files found in .heysops.yaml are decrypted. You may specify multiple files.

   optional arguments:
     -h, --help  show this help message and exit

Usage Examples:

:``heysops decrypt``:
    Will decrypt all files within the configuration file. Useful to run after checking
    out from git.

:``heysops decrypt auth/db_creds.json.sops``: This allows you to decrypt the specified file.

Clean
++++++++

This command cleans your project folder by first encrypting all secrets registered in the configuration file, then
removing all decrypted files. This is useful to run before checking data into a version control system.

Help information:

.. code-block::

   heysops clean --help
   usage: heysops clean [-h]

   optional arguments:
     -h, --help  show this help message and exit


Usage Examples:

:``heysops clean``: Run the encryption command, then remove any decrypted files.

Forget
++++++++

This command removes the specified file(s) from the configuration file. This prevents the tool from interacting with
these files moving forward. It does not remove the entry from the .gitignore.

You must specify a file path. You may specify either the encrypted or decrypted file path and the associated
configuration entry will be removed.

.. code-block::

   heysops forget --help
   usage: heysops forget [-h] FILE [FILE ...]

   positional arguments:
     FILE        The name of the encrypted or decrypted file to forget. You may specify multiple files.

   optional arguments:
     -h, --help  show this help message and exit

Usage examples:

:``heysops forget auth/db_creds.json``: Forget the "auth/db_creds.json" and remove it from the configuration file.
