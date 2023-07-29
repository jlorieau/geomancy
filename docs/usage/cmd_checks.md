(running-checks)=
# Running Checks

## Specifying which checks to run

Geomancy can find checks from files in pre-defined locations, if file
arguments aren't specified, or it can run checks from the files specified as
arguments.

The format of the checks file is specified in the [next section](#file-format).

::::{tab-set}
:::{tab-item} With arguments
The following evaluates the checks listed in ``examples/geomancy.yaml``, if
this file exists.
```shell
$ geo examples/geomancy.yaml
=========================== examples/geomancy.yaml ============================
    checks (12 checks)
[✔]   Environment (2 checks)
[✔]     Check environment variable '$PATH'...passed
[✔]     Check environment variable '$USER'...passed
      Paths (4 checks)
[✔]     ChecksFile (3 checks)
[✔]       Check path 'examples/geomancy.toml'...passed
[✔]       Check path 'examples/pyproject.toml'...passed
[!]       Check path '.missing__.txt'...missing
[✔]   Executables (1 checks)
[✔]     Check executable 'python3>=3.11'...passed
[✔]   PythonPackages (1 checks)
[✔]     Check python package 'geomancy>=0.8'...passed
========================= PASSED. 13 checks in 0.01s ==========================
```
:::
:::{tab-item} Without arguments
When no arguments are specified, geo will search for checks in multiple locations.
```shell
$ geo
================================ geomancy.yaml ================================
    checks (12 checks)
[✔]   Environment (2 checks)
[✔]     Check environment variable '$PATH'...passed
[✔]     Check environment variable '$USER'...passed
      Paths (4 checks)
[✔]     ChecksFile (3 checks)
[✔]       Check path 'examples/geomancy.toml'...passed
[✔]       Check path 'examples/pyproject.toml'...passed
[!]       Check path '.missing__.txt'...missing
[✔]   Executables (1 checks)
[✔]     Check executable 'python3>=3.11'...passed
[✔]   PythonPackages (1 checks)
[✔]     Check python package 'geomancy>=0.8'...passed
========================= PASSED. 13 checks in 0.01s ==========================
```
:::
::::

If no checks files are listed as arguments, geo will search the following file
locations in the current directory, and it wil run all the checks in existing
files: ``.geomancy.yaml``, ``.geomancy.yml``, ``.geomancy.toml``,
``geomancy.yaml``, ``geomancy.yml``, ``geomancy.toml``, ``pyproject.toml``

:::{admonition} Layering and combining checks
:class: tip
Multiple checks files can be run together allowing the mixing and matching
of test sets.

For example, a ``dev`` environment and ``prod`` environment may have common
checks, listed in ``base.yaml``, in addition to environment specific checks
listed in ``dev.yaml`` and ``prod.yaml`` respectively.
```shell
$ geo base.yaml dev.yaml   # 'dev' environment
...
$ geo base.yaml prod.yaml  # 'prod environment
....
```
:::

:::{admonition} Wildcards and glob patterns
:class: tip
The check file arguments support wildcards and glob patterns to run checks from
multiple files at once. For example, the following will run checks in all
files that have the ``geomancy`` filename: ``$ geo geomancy.*``
:::

(configuration)=
## Configuration

As described in the [next section](#file-format), configuration options are
placed in the ``config`` section of checks files or the
``[tool.geomancy.config]`` section of the ``pyproject.toml`` file.

The default configuration options can be listed in
[yaml](https://yaml.org) or [toml](https://toml.io/en/) formats.

::::{tab-set}
:::{tab-item} config (yaml)
```shell
$ geo config --yaml
config:
  CHECKBASE:
    ENV_SUBSTITUTE_DEFAULT: true
    MAX_LEVEL: 10
...
```
:::
:::{tab-item} config (toml)
```shell
$ geo config ---toml
[config]
VERSION='0.9.2'

  [config.CHECKBASE]
  ENV_SUBSTITUTE_DEFAULT=true
  MAX_LEVEL=10...
```
:::
::::

(environment-files)=
## Environment Variables and Files

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

:::{admonition} Layering and combining environments
:class: tip
Layered environments can be created by splitting environment variables
between multiple environment files and invoking the ``-e``/``--env`` flag
multiple times. For example, a ``.base.env`` file could contain environment
variables common to all environments, while a ``.dev.env`` file could
contain environment variables for the 'dev' environment.
:::

:::{admonition} Geomancy within environments
:class: attention
Even though geomancy supports the loading of environment files, it is
recommended that environments are validated using the environment file loading
mechanism used in practice.

For example, if an environment file is used within
[docker compose](https://docs.docker.com/compose/), the geomancy checks should
be tested within the docker compose container.
:::

(environment-files-syntax)=
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

10. Environment file values are substituted according to the
    [substitution](#environment-substitution) rules.
    ```shell
    MYVAR=MYVALUE
    VAR1=$MYVAR      # VAR1=MYVALUE
    ```

(environment-substitution)=
### Substitution

The following rules are followed from
[docker compose](https://docs.docker.com/compose/environment-variables/env-file/#syntax)
for substituting environment variables in values.

1. Environment variables are substituted when preceded by a ``$`` and may or
   may not contain braces. e.g. ``$USER`` or ``${USER}``

2. _Direct substitution_ of braced (``${VAR}``) and unbraced (``$VAR``)
   variables may be done in unquoted or double-quoted values--not single-quoted
   literals.
    ```shell
    MYVAR=MYVALUE
    $MYVAR      # -> MYVALUE
    "${MYVAR}"  # -> MYVALUE
    '${MYVAR}'  # -> ${MYVAR}
    ```
3. _Default value substitution_ will return the default value if the variable
   isn't set or is empty. Defaults can contain spaces in the braced version,
   but not quotes.
   ```shell
   ${MISSING-my default value}   # -> my default value
   ${MISSING:-my default value}  # -> my default value
   $MISSING-default              # -> default
   $MISSING:-default             # -> default
   ```
4. _Error value substitution_ will raise an exception with the given error
   message if an environment variable isn't set or is empty. Errors can contain
   spaces in the braced version, but not quotes
   ```shell
   ${MISSING?no value}   # -> raises EnvironmentError("no value")
   ${MISSING:?no value}  # -> raises EnvironmentError("no value")
   $MISSING?missing      # -> raises EnvironmentError("missing")
   $MISSING:?missing     # -> raises EnvironmentError("missing")
   ```
5. _Replacement value substitution_ will replace a set environment variable
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
