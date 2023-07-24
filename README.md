<img src="https://raw.githubusercontent.com/jlorieau/geomancy/main/assets/geomancy_logo.svg" alt="geomancy" height="120" />

[![pypi version](https://img.shields.io/pypi/v/geomancy.svg)](https://pypi.org/project/geomancy/)
[![python versions](https://img.shields.io/pypi/pyversions/geomancy.svg)](https://pypi.org/project/geomancy/)
[![Black formatting](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

The ``geomancy`` tool makes it easy to check and validate environments, such
as development, testing and production.

Environment checks and tests are helpful for testing external dependencies,
like LaTeX, remote dependencies, like AWS buckets or SSM parameters, or for
checking environments that use the [12-factor](http://12factor.net/) principles.

Currently, ``geomancy`` can:

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

The following is an example ``geomancy`` run with an example checks file.

```shell
$ geo examples/geomancy.toml
========================= examples/geomancy.toml =========================
    checks (10 checks)
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
========================= 11 checks passed in 0.00s ======================
```

## Usage
1. Create a file containing checks. Either

   - ``.geomancy.toml`` in the project root. See the ``examples`` directory for
     examples.

   or

   - ``pyproject.toml`` with checks and config in the ``[tool.geomancy]`` section.

2. Run the geo

   ```shell
   $ geo
   ```

## Format

### Check Groups

Check groups are sections which contain one or more child checks.

| name      | description                                                                                                                                                                   |
|:----------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| desc      | _(Optional)_ The description for the check section                                                                                                                            |
| subchecks | _(Optional)_ Either ``'all'`` to require that all sub-checks pass or ``'any'`` to require that only one sub-check passes.<br>Default: ``'all'``<br>__aliases__: ``condition`` |

##### Examples

The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
``Pyproject``.

```toml
[checks.ChecksFile]
desc = "Checks that at least one checks file exists"
subchecks = "any"

    [checks.ChecksFile.Geomancy]
    desc = "Check for 'geomancy.toml' file"
    checkPath = "examples/geomancy.toml"
    type = "file"

    [checks.ChecksFile.Pyproject]
    desc = "Check for 'pyproject.toml' file"
    checkPath = "examples/pyproject.toml"
    type = "file"
```

The following is the same check group, but in abbreviated format.

```toml
[checks.ChecksFile]
subchecks = "any"

Geomancy = {checkPath = "examples/geomancy.toml", type = "file"}
Pyproject = {checkPath = "examples/pyproject.toml", type = "file"}
```

### Checks

#### checkEnv

Check the existence and, optionally, the value of an environment variable.

| name      | description                                                                                                          |
|:----------|:---------------------------------------------------------------------------------------------------------------------|
| checkEnv  | Environment variable to check, wrapped in curly braces for substitution. <br>__aliases__: ``checkEnv``, ``CheckEnv`` |
| desc      | _(Optional)_ The description for the check                                                                           |
| regex     | _(Optional)_ A regular expression to check against the environment variable value                                    |

##### Examples

```toml
[checks.Environment.Username]
desc = "The current username"
checkEnv = "{USER}"
regex = "[a-z_][a-z0-9_-]*[$]?"
```

#### checkExec

Check the existence and, optionally, the version of available executables or
commands.

| name      | description                                                                                                                                   |
|:----------|:----------------------------------------------------------------------------------------------------------------------------------------------|
| checkExec | Executable to check. Additionally, an optional version check can be added with a test operator. <br>__aliases__: ``checkExec``, ``CheckExec`` |
| desc      | _(Optional)_ The description for the check                                                                                                    |

##### Examples

```toml
[checks.Executables.Ls]
desc = "List files"
checkExec = "ls"
```

```toml
[checks.Executables.Python]
desc = "Python interpreter (version 3.11 or higher)"
checkExec = "python3>=3.11"
```

#### checkPath

Check the existence and type of a path.

| name      | description                                                                                                                                    |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| checkPath | Path to check, which may include environment variables wrapped in curly braces for substitution. <br>__aliases__: ``checkPath``, ``CheckPath`` |
| desc      | _(Optional)_ The description for the check                                                                                                     |
| type      | _(Optional)_ Additionally check whether the path corresponds to a valid ``'file'`` or ``'dir'``.                                               |

##### Examples

```toml
[checks.Environment.Pyproject]
desc = "A project's pyprojectfile"
checkPath = "./pyproject.toml"
path_type = "file"
```

#### checkPythonPkg

Checks whether the python package is installed and, optionally, check its
version.

| name               | description                                                                                                                                                                                                  |
|:-------------------|:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| checkPythonPackage | Python package to check. Additionally, an optional version check can be added with a test operator. <br>__aliases__: ``checkPythonPkg``, ``CheckPythonPkg``, ``checkPythonPackage``, ``CheckPythonPackage``  |
| desc               | _(Optional)_ The description for the check                                                                                                                                                                   |

```toml
[checks.PythonPackages.geomancy]
desc = "Geomancy python package"
checkPythonPkg = "geomancy>=0.1"
```
