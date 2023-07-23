# geomancy

The ``geomancy`` a tool makes it easy to check and validate environments, such
as development, testing and production.

```shell
$ geo examples/geomancy.toml
============================ examples/geomancy.toml ============================
  checks
    Environment
      ✔ Check environment variable 'Path'...passed.
      ✔ Check environment variable 'Username'...passed.
```

## Features
- Checks local environment: environment variables
- Environment variable substitution in values and parameters
- Grouping and nesting of checks

## Usage
1. Create a file containing checks. Either

   - ``.geomancy.toml``in the project root. See the ``examples`` directory for
     examples.

   or

   - ``pyproject.toml`` with check in the ``[tool.geomancy]`` section.

2. Run the geo

   ```shell
   $ geo
   ```

## Format

### checkEnv

Check the existence and, optionally, the value of an environment variable.

| name      | description                                                                                                                  |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------|
| checkEnv  | Environment variable to check, wrapped in curly braces for substitution. <br>__aliases__: ``checkEnv``, ``CheckEnv``         |
| desc      | _(Optional)_ The description for the test                                                                                    |
| regex     | _(Optional)_ A regular expression to test against the environment variable value                                             |

##### Examples

```toml
[checks.Environment.Username]
desc = "The current username"
checkEnv = "{USER}"
regex = "[a-z_][a-z0-9_-]*[$]?"
```

### checkExec

Check the existence and, optionally, the version of available executables or
commands.

| name      | description                                                                                    |
|:----------|:-----------------------------------------------------------------------------------------------|
| checkExec | Executable to check with optional version check. <br>__aliases__: ``checkExec``, ``CheckExec`` |
| desc      | _(Optional)_ The description for the test                                                      |

##### Examples

```toml
[checks.Executables.Python]
desc = "List files"
checkExec = "ls"
```

```toml
[checks.Executables.Python]
desc = "Python interpreter (version 3.11 or higher)"
checkExec = "python>=3.11"
```

### checkPath

Check the existence and type of a path.

| name      | description                                                                                                                                    |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| checkPath | Path to check, which may include environment varaibles wrapped in curly braces for substitution. <br>__aliases__: ``checkPath``, ``CheckPath`` |
| desc      | _(Optional)_ The description for the test                                                                                                      |
| path_type | _(Optional)_ Check whether the path corresponds to a valid ``'file'`` or ``'dir'``.                                                            |

##### Examples

```toml
[checks.Environment.Pyproject]
desc = "A project's pyprojectfile"
checkPath = "./pyproject.toml"
path_type = "file"
```
