# HeySops

A helpful utility for interfacing with sops. Inspired by
[git-secret](https://git-secret.io/)

## Configuration

### Environment Variables

* `SOPS_PATH` - Set the path to the sops binary. By default, it will search the path for the SOPS binary file.

### Configuration File

HeySops uses a configuration file named .heysops.yaml or .heysops.yml. This file should be stored in the root of your
repository, next to your .gitignore file.

## Commands

### Common Arguments

* `-c` - Specify a .heysops.yaml file to use during execution.
* `-f` - Force an action, such as overwriting files.
* `-v` - Display informational log event entries


### Init

* `heysops init` - Creates a .heysops.yaml file in the current directory if it
  does not exist. This must be run before other commands. You can have
  multiple .heysops.yaml within a folder structure.

### Encrypt

* `heysops encrypt` - Encrypts all files that were previously encrypted with
  this tool. Uses the .heysops.yaml file in the local directory. If
  .heysops.yaml is not found in the current directory, it traverses upwards
  until it finds one. If it doesn't find one, it warns and exits.
* `heysops encrypt [file]` - Encrypts the specified file, creating a new
  file alongside it with the `.sops` extension.
* `heysops encrypt --type {json,yaml,dotenv,binary} [file]` - Encrypts the
  specified file, creating a new file alongside it with the `.sops` extension.
  Passes the specified `--type` to sops's `--input-type` argument. Will use the
  same type on decryption.


### Decrypt

* `heysops decrypt` - If no files are specified, it looks for a file
  named .heysops.yaml in the local directory. If .heysops.yaml is not found
  in the current directory, it traverses upwards
  until it finds one. If it doesn't find one, it warns and exits.
  Prompts if the decrypted file name already exists.
* `heysops decrypt [file]` - Decrypts the specific file.
  Prompts if the decrypted file name already exists.

### Clean

* `heysops clean` - Removes all decrypted files if we have an encrypted copy.

### Forget

* `heysops forget [file]` - Untrack a file within .heysops.yaml. This will
  leave the file on the system and no longer interact with it through other
  commands.

