(running-environments)=
# Running Environments

Geomancy can load environment files and run commands from within these
environment.

The ``run`` subcommand will run commands in a separate process, and environment
files are loaded with the ``-e``/``-env`` option for each environment.

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

:::{caution}
Including environment variable references in commands will expand them before
running the command within the environment. For example, if the ``.env`` file
specified ``ENV=dev``, then ``$ENV`` variable would not be set in the following
command.

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

(environment-files)=
## Environment Files

Environment variables can be loaded from one or more environment files
(a.k.a dotenv files) with the ``-e``/``--env`` flag.

```shell
$ geo -e .base.env -e .dev.env
```

By default, existing environment variables, or environment variables set
by preceding env files, are not overwritten. To change this behavior,
use the ``--overwrite`` flag.

```shell
$ geo -e .base.env -e .dev.env --overwrite
```

:::{tip}
Layered environments can be created by splitting environment variables
between multiple environment files and invoking the ``-e``/``--env`` flag
multiple times. For example, a ``.base.env`` file could contain environment
variables common to all environments, while a ``.dev.env`` file could
contain environment variables for the 'dev' environment.
:::

:::{attention}
Even though geomancy supports the loading of environment files, it is
recommended that environments are validated using the environment file loading
mechanism used in practice.

For example, if an environment file is used within
[docker compose](https://docs.docker.com/compose/), the geomancy should be
tested within the docker compose container.
:::

### Syntax

Environment files are a superset of the
[docker compose](https://docs.docker.com/compose/environment-variables/env-file/#syntax)
environment file rules. Specifically,

1. Environment variable names may contain letters (``A-Z`` or ``a-z``),
   numbers (``0-9``) and underscores (``_``), but the first character must be a
   letter (``A-Z`` or ``a-z``)
2. Lines beginning with a ``#`` are considered a comment and ignored
3. Blank lines are ignored
4. Each line represents an environment variable name-value pair. Values may
   be quoted.
    ```shell
    VAR=VAL    # -> VAL
    VAR="VAL"  # -> VAL
    VAR='VAL'  # -> VAL
    ```
5. Inline comments must be preceded by a space
   ```shell
   VAR=VALUE # comment       # -> VALUE
   VAR=VALUE# not a comment  # -> VALUE# not a comment
   ```
6. Comments for quoted values must follow the quote
    ```shell
   VAR="VALUE # not a comment"  # -> VALUE # not a comment
   VAR="VALUE"  # comment       # -> VALUE
    ```
7. Single-quoted values are taken literally
    ```shell
    VAR='$OTHER'    # -> $OTHER
    VAR='${OTHER}'  # -> ${OTHER}
    ```
8. Quotes can be escaped
    ```shell
    VAR='Let\'s go!'             # -> Let's go!
    VAR="{\"hello\": \"json\"}"  # -> {"hello": "json"}
    ```
9. Shell escape sequences (``\n``, ``\t``, ``\r``, ``\\``) are supported in
   double-quoted values
    ```shell
    VAR="some\tvalue"  # -> some    value
    VAR='some\tvalue'  # -> some\tvalue
    VAR=some\tvalue     # -> some\tvalue
    ```
10. _Direct substitution_ of braced (``${VAR}``) and unbraced (``$VAR``)
   variables in unquoted or double-quoted values--not single-quoted literals.
    ```shell
    MYVAR=MYVALUE
    VAR1=$MYVAR      # -> MYVALUE
    VAR2="${MYVAR}"  # -> MYVALUE
    VAR3='${MYVAR}'  # -> ${MYVAR}
    ```
11. _Default value substitution_ will return the default value if the variable
    isn't set or is empty. Defaults can contain spaces in the braced version,
    but not quotes.
    ```shell
    ${MISSING-my default value}   # -> my default value
    ${MISSING:-my default value}  # -> my default value
    $MISSING-default              # -> default
    $MISSING:-default             # -> default
    ```
12. _Error value substitution_ will raise an exception with the given error
    message if an environment variable isn't set or is empty. Errors can contain
   spaces in the braced version, but not quotes
    ```shell
    ${MISSING?no value}   # -> raises EnvironmentError("no value")
    ${MISSING:?no value}  # -> raises EnvironmentError("no value")
    $MISSING?missing      # -> raises EnvironmentError("missing")
    $MISSING:?missing     # -> raises EnvironmentError("missing")
    ```
13. _Replacement value substitution_ will replace a set environment variable
    with the replacement value, otherwise it will produce an empty string.
    Replacements can contain spaces in the braced version, but not quotes
    ```shell
    MYVAR=MYVALUE
    ${MYVAR+replaced}   # -> replaced
    ${MYVAR:+replaced}  # -> replaced
    $MYVAR+replaced     # -> replaced
    $MYVAR:+replaced    # -> replaced
    ${MISSING+replaced} # ""
    ${MISSING+replaced} # ""
    ```
