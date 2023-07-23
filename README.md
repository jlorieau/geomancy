# geomancy

The ``geomancy`` tool makes it easy to check and validate environments, such
as development, testing and production.

Currently, ``geomancy`` can check that:
- [environment variables](#checkenv) are properly set
- [file and directory paths](#checkpath) exist
- [executables](#checkexec) are available and, optionally, of the correct version
- [check grouping](#check-groups) and conditional evaluation
- supports setting values with environment variable substitution.
  ex: ``checkPath: {HOME}/.geomancy.toml``

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

Check groups are sections which contain one or more sub-checks.

| name      | description                                                                                                                                     |
|:----------|:------------------------------------------------------------------------------------------------------------------------------------------------|
| desc      | _(Optional)_ The description for the check section                                                                                              |
| condition | _(Optional)_ Either ``'all'`` to require that all sub-checks pass or ``'any'`` to require that only one sub-check passes.<br>Default: ``'all'`` |

##### Examples

The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
``Pyproject``.

```toml
[checks.ChecksFile]
    desc = "Checks that at least one checks file exists"
    condition = "any"

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
    condition = "any"

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
| checkPath | Path to check, which may include environment varaibles wrapped in curly braces for substitution. <br>__aliases__: ``checkPath``, ``CheckPath`` |
| desc      | _(Optional)_ The description for the check                                                                                                     |
| type      | _(Optional)_ Additionally check whether the path corresponds to a valid ``'file'`` or ``'dir'``.                                               |

##### Examples

```toml
[checks.Environment.Pyproject]
desc = "A project's pyprojectfile"
checkPath = "./pyproject.toml"
path_type = "file"
```
