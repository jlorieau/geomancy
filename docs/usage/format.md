(file-format)=
# File format for Checks

The checks file is formatted in [yaml](https://yaml.org) or [toml](https://toml.io/en/),
and it contains a listing of checks and, optionally, configuration options
for ``geomancy``.

## Filenames

The checks file may be a dedicated file for ``geomancy``, such as a
``.geomancy.yaml`` or ``.geomancy.toml`` file in the project root
directory, or it may be incorporated as part of a ``pyproject.toml`` file
under the ``[tool.geomancy]`` section.

::::{tab-set}
:::{tab-item} geomancy.yaml
```yaml
checks:
  Username:
    desc: The current username
    checkEnv: "{USER}"
    regex: "[a-z_][a-z0-9_-]*[$]?"
```
:::
:::{tab-item} geomancy.toml
```toml
[checks.Username]
desc = "The current username"
checkEnv = "{USER}"
regex = "[a-z_][a-z0-9_-]*[$]?"
```
:::
:::{tab-item} pyproject.toml
```toml
[tool.geomancy.checks.Username]
desc = "The current username"
checkEnv = "{USER}"
regex = "[a-z_][a-z0-9_-]*[$]?"
```
:::
::::

## Nesting and Listing Checks

Checks can be grouped into sections of related checks, and the pass condition
for child checks can be customized.

::::{tab-set}
:::{tab-item} geomancy.yaml
By default, all child checks must pass for the parent check to pass.
In this example, the parent check, ``ChecksFile``, may pass if any of the
3 child checks pass--either ``GeomancyToml``, ``PyprojectToml`` or
``GeomancyYaml``. This condition is specified by ``subchecks = any`` option.

```yaml
checksFile:
  desc: Checks that at least on of the files exists
  subchecks: any

  GeomancyToml:
    desc: Check for 'geomancy.toml' file
    checkPath: examples/geomancy.toml
    type: file
  PyprojectToml:
    desc: Check for 'pyproject.toml' file
    checkPath: examples/pyproject.toml
    type: file
  GeomancyYaml:
    desc: Check for 'geomancy.yaml' file
    checkPath: examples/geomancy.yaml
    type: file
```
:::
:::{tab-item} geomancy.toml
By default, all child checks must pass for the parent check to pass.
In this example, the parent check, ``ChecksFile``, may pass if any of the
3 child checks pass--either ``GeomancyToml``, ``PyprojectToml`` or
``GeomancyYaml``. This condition is specified by ``subchecks = "any"`` option.

```toml
[checks.ChecksFile]
desc = "Checks that at least one checks file exists"
subchecks = "any"

[checks.ChecksFile.GeomancyToml]
desc = "Check for 'geomancy.toml' file"
checkPath = "examples/geomancy.toml"
type = "file"

[checks.ChecksFile.PyprojectToml]
desc = "Check for 'pyproject.toml' file"
checkPath = "examples/pyproject.toml"
type = "file"

[checks.ChecksFile.GeomancyYaml]
desc = "Check for 'geomancy.yaml' file"
checkPath = "examples/geomancy.yaml"
type = "file"
```
:::
:::{tab-item} pyproject.toml
By default, all child checks must pass for the parent check to pass.
In this example, the parent check, ``ChecksFile``, may pass if any of the
3 child checks pass--either ``GeomancyToml``, ``PyprojectToml`` or
``GeomancyYaml``. This condition is specified by ``subchecks = "any"`` option.

```toml
[tool.geomancy.checks.ChecksFile]
desc = "Checks that at least one checks file exists"
subchecks = "any"

[tool.geomancy.checks.ChecksFile.GeomancyToml]
desc = "Check for 'geomancy.toml' file"
checkPath = "examples/geomancy.toml"
type = "file"

[tool.geomancy.checks.ChecksFile.PyprojectToml]
desc = "Check for 'pyproject.toml' file"
checkPath = "examples/pyproject.toml"
type = "file"

[tool.geomancy.checks.ChecksFile.GeomancyYaml]
desc = "Check for 'geomancy.yaml' file"
checkPath = "examples/geomancy.yaml"
type = "file"
```

:::
::::

## Configuration

Checks files may optionally include configuration settings for geomancy. The
[config](#configuration) lists the current default configuration.

::::{tab-set}
:::{tab-item} geomancy.yaml
Configuration settings are specified the ``config`` section.
```yaml
config:
  CHECKBASE:
    ENV_SUBSTITUTE_DEFAULT: true
```
:::
:::{tab-item} geomancy.toml
Configuration settings are specified the ``[config]`` section.
```toml
[config]
[config.CHECKBASE]
ENV_SUBSTITUTE_DEFAULT = true
```
:::
:::{tab-item} pyproject.toml
Configuration settings are specified in the ``[tool.geomancy.config]`` section.
```toml
[tool.geomancy.config]
[tool.geomancy.config.CHECKBASE]
ENV_SUBSTITUTE_DEFAULT = true
```
:::
::::

## Checks

The following describes the various checks and their options.

### checkEnv

Check the existence and, optionally, the value of an environment variable.

:checkEnv: Environment variable to check, wrapped in curly braces for
substitution. <br>
__aliases__: ``checkEnv``, ``CheckEnv``
:desc: _(Optional)_ The description for the check
:regex: _(Optional)_ A regular expression to check against the environment
variable value

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The ``checkEnv`` check in YAML format.
```yaml
checks:
  Environment:
    Username:
      desc: The current username
      checkEnv: "{USER}"
      regex: "[a-z_][a-z0-9_-]*[$]?"
```
:::
:::{tab-item} Example 2 (toml)
The ``checkEnv`` check in TOML format.
```toml
[checks.Environment.Username]
desc = "The current username"
checkEnv = "{USER}"
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

### checkExec

Check the existence and, optionally, the version of available executables or
commands.

:checkExec: Executable to check. Additionally, an optional version check
can be added with a test operator. <br>
__aliases__: ``checkExec``, ``CheckExec``
:desc: _(Optional)_ The description for the check

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

### checkPath

Check the existence and, optionally, the type of a path.

:checkPath: Path to check, which may include environment variables wrapped
in curly braces for substitution. <br>
__aliases__: ``checkPath``, ``CheckPath``
:desc: _(Optional)_ The description for the check
:type: _(Optional)_ Additionally check whether the path corresponds to a
valid ``'file'`` or ``'dir'``.

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

### checkPythonPkg

Checks whether the python package is installed and, optionally, check its
version.

:checkPythonPkg: Python package to check. Additionally, an optional version
check can be added with a test operator. <br>
__aliases__: ``checkPythonPkg``, ``CheckPythonPkg``,
``checkPythonPackage``, ``CheckPythonPackage``
:desc: _(Optional)_ The description for the check

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

### Check Groups

Check groups are sections which contain one or more child checks.

:desc: _(Optional)_ The description for the check section
:subchecks: _(Optional)_ Either ``'all'`` to require that all sub-checks
pass or ``'any'`` to require that only one sub-check passes.<br>
Default: ``'all'``<br>
__aliases__: ``condition``

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
``Pyproject``.
```yaml
checksFiles:
  desc: Checks that at least one checks file exists

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
