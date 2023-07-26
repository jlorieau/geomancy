<!-- start logo -->
<img src="https://raw.githubusercontent.com/jlorieau/geomancy/main/docs/_static/geomancy_logo.svg" alt="geomancy logo" height="150px"/>
<!-- end logo -->

<!-- start badges -->
[![pypi version](https://img.shields.io/pypi/v/geomancy.svg)](https://pypi.org/project/geomancy/)
[![python versions](https://img.shields.io/pypi/pyversions/geomancy.svg)](https://pypi.org/project/geomancy/)
[![Black formatting](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/geomancy/badge/?version=latest)](https://geomancy.readthedocs.io/en/latest/?badge=latest)
<!-- end badges -->
<!-- start intro -->
The ``geomancy`` tool makes it easy to check and validate environments, such
as development, testing and production.

Environment checks and tests are helpful for testing the correct setting
of environment variables, the installation and versions of installed
executables, the state of external dependencies, like LaTeX packages, or cloud
resources, or for checking environments that use the
[12-factor](http://12factor.net/) principles.
<!-- end intro -->

## Quickstart
<!-- start quickstart -->
Create a ``.geomancy.yaml`` file with checks.

```yaml
checks:
    Environment:
        desc: Check environment variables common to all development environments

        Username:
            desc: The current username
            checkEnv: "{USER}"
            regex: "[a-z_][a-z0-9_-]*[$]?"

    Paths:
      desc: Checks the existence of needed files and directories
      subchecks: any  # at least one of the files must be present

          Geomancy:
              desc: Check for the 'geomancy.toml' file
              checkPath: examples/geomancy.toml
              type: file
          Pyproject:
              desc: Check for 'pyproject.toml' file
              checkPath: examples/pyproject.toml
              type: file

    Executables:
        desc: Check the availability of commands and their versions

        Python:
            desc: Python interpreter ver 3.11 or higher
            checkExec: python3>=3.11
```

Use ``geo`` to run the checks.

```shell
$ geo
=============================== .geomancy.toml ================================
    checks (9 checks)
[✔]   Environment (1 checks)
[✔]     Check environment variable '{USER}'...passed
[✔]   Paths (2 checks)
[✔]     Check path 'examples/geomancy.toml'...passed
[✔]     Check path 'examples/pyproject.toml'...passed
[✔]   Executables (1 checks)
[✔]     Check executable 'python3>=3.11'...passed
========================== PASSED.  8 checks in 0.01s =========================
```
(By default, ``geomancy`` will search ``.geomancy.y[a]ml``, ``geomancy.y[a]ml``
``.geomancy.toml``, ``geomancy.toml`` and ``pyproject.toml``.)
<!-- end quickstart -->

## Features
<!-- start features -->
``geomancy`` can:

- __Environment variables__. Check environment variables are properly set and,
  optionally, check that they have valid values
  ([checkEnv](https://geomancy.readthedocs.io/en/latest/usage/index.html#checkenv))
- __Paths__. Check file and directory path existence
  ([checkPath](https://geomancy.readthedocs.io/en/latest/usage/index.html#checkpath))
- __Executables__. Check executables are available and, optionally, have the
  minimum or correct versions
  ([checkExec](https://geomancy.readthedocs.io/en/latest/usage/index.html#checkexec))
- __Python Packages__. Check python packages are available and, optionally,
  have the minimum or correct versions
  ([checkPythonPkg](https://geomancy.readthedocs.io/en/latest/usage/index.html#checkpythonpkg))
- __Group Checks__. Nested group checks with conditional (all or any) pass
  criteria ([groups of checks](https://geomancy.readthedocs.io/en/latest/usage/index.html#check-groups))
- __Environment Substitution__. Substitute parameter values from environment
  variables. ex: ``checkPath: {HOME}/.geomancy.toml``
- __Multiple Formats__. Checks files can be in yaml (e.g. ``.geomancy.yaml``)
  or in [toml](https://toml.io/en/) (e.g. ``.geomancy.toml`` or
  ``pyproject.toml``)
<!-- end features -->

## Documentation

For full documentation please see https://geomancy.readthedocs.io/en/latest.


## Bugs or Requests
Please use the [GitHub issue tracker](https://github.com/jlorieau/geomancy/issues)
to submit bugs or request features.

## License

Copyright Justin Lorieau and others, 2023.

Distributed under the terms of the [MIT license](LICENSE).
geomancy is free and open source software.
