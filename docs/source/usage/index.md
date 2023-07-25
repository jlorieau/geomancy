# Usage

## Format

### checkEnv

Check the existence and, optionally, the value of an environment variable.

:checkEnv: Environment variable to check, wrapped in curly braces for
    substitution. <br>
    __aliases__: ``checkEnv``, ``CheckEnv``
:desc: _(Optional)_ The description for the check
:regex: _(Optional)_ A regular expression to check against the environment
    variable value

::::{tab-set}

:::{tab-item} Example 1
```toml
[checks.Environment.Username]
desc = "The current username"
checkEnv = "{USER}"
regex = "[a-z_][a-z0-9_-]*[$]?"
```
:::

:::{tab-item} Example 2 (abbreviated)
```toml
[checks.Environment]
Username = {checkEnv = "{USER}", regex="[a-z_][a-z0-9_-]*[$]?"}
```
:::

::::


### checkExec

Check the existence and, optionally, the version of available executables or
commands.

:checkExec: Executable to check. Additionally, an optional version check
    can be added with a test operator. <br>
    __aliases__: ``checkExec``, ``CheckExec``
:desc: _(Optional)_ The description for the check

::::{tab-set}

:::{tab-item} Example 1
```toml
[checks.Executables.Ls]
desc = "List files"
checkExec = "ls"
```
:::

:::{tab-item} Example 2 (with version)
```toml
[checks.Executables.Python]
desc = "Python interpreter (version 3.11 or higher)"
checkExec = "python3>=3.11"
```
:::

:::{tab-item} Example 3 (abbreviated)
```toml
[checks.Executables]
Python = {checkExec = "python3>=3.11"}
```
:::

::::


### checkPath

Check the existence and, optionally, the type of a path.

:checkPath: Path to check, which may include environment variables wrapped
    in curly braces for substitution. <br>
    __aliases__: ``checkPath``, ``CheckPath``
:desc: _(Optional)_ The description for the check
:type: _(Optional)_ Additionally check whether the path corresponds to a
    valid ``'file'`` or ``'dir'``.

::::{tab-set}

:::{tab-item} Example 1
```toml
[checks.Environment.Pyproject]
desc = "A project's pyprojectfile"
checkPath = "./pyproject.toml"
path_type = "file"
```
:::

:::{tab-item} Example 2 (abbreviated)
```toml
[checks.Environment]
Pyproject = {checkPath = "./pyproject.toml", path_type = "file"}
```
:::

::::

### checkPythonPkg

Checks whether the python package is installed and, optionally, check its
version.

:checkPythonPkg: Python package to check. Additionally, an optional version
    check can be added with a test operator. <br>
    __aliases__: ``checkPythonPkg``, ``CheckPythonPkg``,
    ``checkPythonPackage``, ``CheckPythonPackage``
:desc: _(Optional)_ The description for the check

::::{tab-set}

:::{tab-item} Example 1
```toml
[checks.PythonPackages.geomancy]
desc = "Geomancy python package"
checkPythonPkg = "geomancy>=0.1"
```
:::

:::{tab-item} Example 2 (abbreviated)
```toml
[checks.PythonPackages]
geomancy = {checkPythonPkg = "geomancy>=0.1"}
```
:::

::::


### Check Groups

Check groups are sections which contain one or more child checks.

:desc: _(Optional)_ The description for the check section
:subchecks: _(Optional)_ Either ``'all'`` to require that all sub-checks
    pass or ``'any'`` to require that only one sub-check passes.<br>
    Default: ``'all'``<br>
    __aliases__: ``condition``

::::{tab-set}

:::{tab-item} Example 1
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
:::

:::{tab-item} Example 2 (abbreviated)
The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
``Pyproject``, in abbreviated format.

```toml
[checks.ChecksFile]
subchecks = "any"

Geomancy = {checkPath = "examples/geomancy.toml", type = "file"}
Pyproject = {checkPath = "examples/pyproject.toml", type = "file"}
```

:::

::::
