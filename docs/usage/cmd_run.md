(running-environments)=
# Running Environments

Geomancy can load [environment files](#environment-files) and run commands
from within these environments.

The ``run`` subcommand will run commands in a separate process, and environment
files are loaded with the ``-e``/``-env`` option for each environment.
See [Environment Files](#environment-files) for the syntax of environment files.

```shell
$ geo run -e [env_file] -- [cmd]
```

The following examples shows commands with arguments.

::::{tab-set}
:::{tab-item} Example
The following runs echo and grep in an environment loaded with the ``.env``
file.
```shell
$ geo run -e .env -- echo "My first test" | grep -e "test"
My first test
```
:::
:::{tab-item} Example (abbreviated)
The following is a command that does not produce option conflicts with geo--
i.e. it does not use a `-e` flag, which could be captured by geo.
```shell
$ geo run -e .env uname
Darwin
```
:::
::::

:::{admonition} Shell expansions
:class: caution
Including environment variable references in commands will expand them before
running the command within the environment. For example, if the ``.env`` file
specified ``ENV=dev``, then ``$ENV`` variable would not be printed to the
shell with the following command.

```shell
$ geo run -e .env -- echo $ENV
```

Instead the value of ``ENV`` can be retrieve from the environment's ``env``
command.

```shell
$ geo run -e .env -- env|grep ENV
ENV=dev
```
:::

