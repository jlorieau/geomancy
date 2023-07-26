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
[✔]     Check environment variable '{PATH}'...passed
[✔]     Check environment variable '{USER}'...passed
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
[✔]     Check environment variable '{PATH}'...passed
[✔]     Check environment variable '{USER}'...passed
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
files:

- ``.geomancy.yaml``
- ``.geomancy.yml``
- ``.geomancy.toml``
- ``geomancy.yaml``
- ``geomancy.yml``
- ``geomancy.toml``
- ``pyproject.toml``

:::{tip}
The check file arguments support globs and wildcards to run checks from
multiple files at once. For example, the following will run checks in all
files that have the ``geomancy`` filename: ``$ geo geomancy.*``
:::

## Configuring geomancy

As described in the [next section](#file-format), configuration options are
placed in the ``config`` section of checks files or the
``[tool.geomancy.config]`` section of the ``pyproject.toml`` file.

The default configuration options can be listed in
[yaml](https://yaml.org) or [toml](https://toml.io/en/) formats.

::::{tab-set}
:::{tab-item} config-yaml
```shell
$ geo --config-yaml
config:
  CHECKBASE:
    ENV_SUBSTITUTE_DEFAULT: true
    MAX_LEVEL: 10
...
```
:::
:::{tab-item} config-toml
```shell
$ geo --config-toml
[config]
VERSION='0.9.2'

  [config.CHECKBASE]
  ENV_SUBSTITUTE_DEFAULT=true
  MAX_LEVEL=10...
```
:::
::::

## Environment variables
