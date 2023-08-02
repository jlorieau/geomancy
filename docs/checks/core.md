# Core

The following describes core checks and their options.

:::{versionchanged} 0.9.3
Environment variables are now referenced by the name preceded by a ``$`` and
optional braces. e.g. ``$USER`` or ``${USER}``
:::

## checkEnv

Check the existence and, optionally, the value of an environment variable.

:::{card}
Parameters
^^^
`checkEnv`: str
: Environment variable to check, wrapped in curly braces for substitution. <br>
  __aliases__: ``checkEnv``, ``CheckEnv``

```{include} snippets/base_args.md
```

`regex`: str (Optional)
: A regular expression to check against the environment variable
  value
:::

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The ``checkEnv`` check in YAML format.
```yaml
checks:
  Environment:
    Username:
      desc: The current username
      checkEnv: "$USER"
      regex: "[a-z_][a-z0-9_-]*[$]?"
```
:::
:::{tab-item} Example 2 (toml)
The ``checkEnv`` check in TOML format.
```toml
[checks.Environment.Username]
desc = "The current username"
checkEnv = "$USER"
regex = "[a-z_][a-z0-9_-]*[$]?"
```
:::
:::{tab-item} Example 3 (toml)
The ``checkEnv`` check in abbreviated TOML format.
```toml
[checks.Environment]
Username = { checkEnv = "{USER}", regex = "[a-z_][a-z0-9_-]*[$]?" }
```
:::
::::

## checkExec

Check the existence and, optionally, the version of available executables or
commands.

:::{card}
Parameters
^^^
`checkExec`: str
: Executable to check. Additionally, an optional version check can be added
  with a test operator. <br>
  __aliases__: ``checkExec``, ``CheckExec``

```{include} snippets/base_args.md
```
:::

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The ``checkExec`` check in YAML format.
```yaml
checks:
  Ls:
    desc: List files
    checkExec: "ls"
```
:::
:::{tab-item} Example 2 (yaml)
The ``checkExec`` check with version checking in YAML format.
```yaml
checks:
  Python:
    desc: Python interpreter (version 3.11 or higher)
    checkExec: "python3>=3.11"
```
:::
:::{tab-item} Example 3 (toml)
The ``checkExec`` check with version checking in TOML format.
```toml
[checks.Executables.Python]
desc = "Python interpreter (version 3.11 or higher)"
checkExec = "python3>=3.11"
```
:::
:::{tab-item} Example 4 (toml)
The ``checkExec`` check with version checking in abbreviated TOML format.
```toml
[checks.Executables]
Python = { checkExec = "python3>=3.11" }
```
:::
::::

## checkPath

Check the existence and, optionally, the type of path.

:::{card}
Parameters
^^^
`checkPath`: str
: Path to check, which may include environment variables for substitution. <br>
  __aliases__: ``checkPath``, ``CheckPath``

```{include} snippets/base_args.md
```

`type`: str (Optional)
: Additionally check whether the path corresponds to a valid ``'file'`` or
  ``'dir'``.
:::

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The ``checkPath`` check in YAML format.
```yaml
checks:
  Pyproject:
    desc: A project's pyprojectfile
    checkPath: ./pyproject.toml
    type: file
```
:::
:::{tab-item} Example 2 (toml)
The ``checkPath`` check in TOML format.
```toml
[checks.Environment.Pyproject]
desc = "A project's pyprojectfile"
checkPath = "./pyproject.toml"
type = "file"
```
:::
:::{tab-item} Example 3 (toml)
The ``checkPath`` check in abbreviated TOML format.
```toml
[checks.Environment]
Pyproject = { checkPath = "./pyproject.toml", type = "file" }
```
:::
::::

## checkPlatform

Check the current platform and, optionally, its minimum version.

:::{card}
Parameters
^^^
`checkPlatform`: str
: Operating system to check. Additionally, an optional version check can be added
  with a test operator. <br>
  __aliases__: ``checkOS``, ``checkPlatform``

```{include} snippets/base_args.md
```
:::

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The ``checkPlatform`` check in YAML format.
```yaml
check:
  OperatingSystem:
    desc: Check the minimum operating system versions
    subchecks: any

    checkMacOS:
      desc: MacOS 10.9 or later (released 2013)
      checkOS: "macOS >= 10.9"
    checkLinuxOS:
      desc: Linux 4.0 or later (released 2015)
      checkOS: "Linux >= 3.0"
    checkWindows:
      desc: Windows 10 or later (released 2015)
      checkOS: "Windows >= 10"
```
:::
:::{tab-item} Example 2 (toml)
The ``checkPlatfor`` check in TOML format.
```toml
[checks.OperatingSystem]
desc = "Check the minimum operating system versions"
subchecks = "any"

    [checks.OperatingSystem.checkMacOS]
    desc = "MacOS 10.9 or later (released 2013)"
    checkOS = "macOS >= 10.9"

    [checks.OperatingSystem.checkLinuxOS]
    desc = "Linux 4.0 or later (released 2015)"
    checkOS = "Linux >= 3.0"

    [checks.OperatingSystem.checkWindows]
    desc = "Windows 10 or later (released 2015)"
    checkOS = "Windows >= 10"
```
:::
:::{tab-item} Example 3 (toml)
The ``checkPlatform`` check in abbreviated TOML format.
```toml
[checks.OperatingSystem]
desc = "Check the minimum operating system versions"
subchecks = "any"

checkMacOS = {desc = "MacOS 10.9 or later (released 2013)", checkOS = "macOS >= 10.9"}
checkLinuxOS = {desc = "Linux 4.0 or later (released 2015)", checkOS = "Linux >= 3.0"}
checkWindows = {desc = "Windows 10 or later (released 2015)", checkOS = "Windows >= 10"}
```
:::
::::

## checkPythonPkg

Checks whether the python package is installed and, optionally, check its
version.

:::{card}
Parameters
^^^
`checkPythonPkg`: str
: Python package to check. Additionally, an optional version check can be added
  with a test operator. <br>
  __aliases__: ``checkPythonPkg``, ``CheckPythonPkg``, ``checkPythonPackage``,
  ``CheckPythonPackage``

```{include} snippets/base_args.md
```
:::

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The ``checkPythonPkg`` check in YAML format.
```yaml
checks:
  PythonPackages:
    geomancy:
      desc: Geomancy python package
      checkPythonPkg: "geomancy>=0.1"
```
:::
:::{tab-item} Example 2 (toml)
The ``checkPythonPkg`` check in TOML format.
```toml
[checks.PythonPackages.geomancy]
desc = "Geomancy python package"
checkPythonPkg = "geomancy>=0.1"
```
:::
:::{tab-item} Example 3 (toml)
The ``checkPythonPkg`` check in abbreviated TOML format.
```toml
[checks.PythonPackages]
geomancy = { checkPythonPkg = "geomancy>=0.1" }
```
:::
::::

## Check Groups

Check groups are sections which contain one or more child checks.

:::{card}
Parameters
^^^
`desc`: str (Optional)
: The description for the check group

`subchecks`: str (Optional)
: The pass condition for the sub-checks of the group. Can be either ``'all'``
  to require that all sub-checks pass or ``'any'`` to require that only one
  sub-check passes.<br>
  __default__: ``'all'``<br>
  __aliases__: ``condition``
:::

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
``Pyproject``.
```yaml
checksFiles:
  desc: Checks that at least one checks file exists
  subchecks: any

  Geomancy:
    desc: Check for the 'geomancy.toml' file
    checkPath: examples/geomancy.toml
    type: file
  Pyproject:
    desc: Check for 'pyproject.toml' file
    checkPath: examples/pyproject.toml
    type: file
```
:::
:::{tab-item} Example 2 (toml)
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
:::{tab-item} Example 3 (toml)
The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
``Pyproject``, in abbreviated format.
```toml
[checks.ChecksFile]
subchecks = "any"

Geomancy = { checkPath = "examples/geomancy.toml", type = "file" }
Pyproject = { checkPath = "examples/pyproject.toml", type = "file" }
```
:::
::::
