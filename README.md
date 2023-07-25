<!-- start intro -->
![geomancy logi](https://raw.githubusercontent.com/jlorieau/geomancy/main/assets/geomancy_logo.png)

[![pypi version](https://img.shields.io/pypi/v/geomancy.svg)](https://pypi.org/project/geomancy/)
[![python versions](https://img.shields.io/pypi/pyversions/geomancy.svg)](https://pypi.org/project/geomancy/)
[![Black formatting](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The ``geomancy`` tool makes it easy to check and validate environments, such
as development, testing and production.

Environment checks and tests are helpful for testing external dependencies,
like LaTeX, remote dependencies, like AWS buckets or SSM parameters, or for
checking environments that use the [12-factor](http://12factor.net/) principles.
<!-- end intro -->

## Features
<!-- start features -->
``geomancy`` can:

- __Environment variables__. Check environment variables are properly set and,
optionally, check that they have valid values ([checkEnv](#checkenv))
- __Paths__. Check file and directory path existence ([checkPath](#checkpath))
- __Executables__. Check executables are available and, optionally, have the
  minimum or correct versions ([checkExec](#checkexec))
- __Python Packages__. Check python packages are availabile and, optionally,
  have the minimum or correct versions ([checkPythonPkg](#checkpythonpkg))
- __Group Checks__. Nested group checks with conditional (all or any) pass
  criteria ([groups of checks](#check-groups))
- __Environment Substitution__. Subsitute parameter values from environment
  variables. ex: ``checkPath: {HOME}/.geomancy.toml``
<!-- end features -->

## Quickstart
<!-- start quickstart -->
Create a ``.geomancy.[toml](https://toml.io/en/)`` file with checks.

```toml
[checks.Environment]
desc = "Check environment variables common to all development environments"

    [checks.Environment.Username]
    desc = "The current username"
    checkEnv = "{USER}"
    regex = "[a-z_][a-z0-9_-]*[$]?"

[checks.Paths]
desc = "Checks the existence of needed files and directories"
subchecks = "any"  # at least one sub-check should pass

    [checks.Paths.Geomancy]
    desc = "Check for 'geomancy.toml' file"
    checkPath = "examples/geomancy.toml"
    type = "file"

    [checks.Paths.Pyproject]
    desc = "Check for 'pyproject.toml' file"
    checkPath = "examples/pyproject.toml"
    type = "file"

[checks.Executables]
desc = "Check the availability of commands and their versions"

    [checks.Executables.Python]
    desc = "Python interpreter"
    checkExec = "python3>=3.11"

[checks.PythonPackages]
desc = "Check the presence and, optional, the version of python packages"

    [checks.PythonPackages.geomancy]
    desc = "Geomancy python package"
    checkPythonPkg = "geomancy>=0.1"
```

By default, ``geomancy`` will search ``.geomancy.toml``, ``geomancy.toml`` and
``pyproject.toml``.

Use ``geo`` to run the checks

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
[✔]   PythonPackages (1 checks)
[✔]     Check python package 'geomancy>=0.1'...passed
======================= PASSED. 10 checks in 0.01s =======================
```
<!-- end quickstart -->

## Usage
<!-- start usage -->
1. Create a file containing checks. Either

   - ``.geomancy.toml`` in the project root. See the ``examples`` directory for
     examples.

   or

   - ``pyproject.toml`` with checks and config in the ``[tool.geomancy]`` section.

2. Run the geo

   ```shell
   $ geo
   ```
<!-- end usage -->
