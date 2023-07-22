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

Tests the existence and, optionally, the value of an environment variable.

| name      | description                                                                                                                  |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------|
| checkEnv  | Environment variable to check, wrapped in curly braces for substitution. <br>__aliases__: ``checkEnv``, ``CheckEnv``         |
| desc      | _(Optional)_ The description for the test                                                                                    |
| regex     | _(Optional)_ A regular expression to test against the environment variable value                                             |

##### Example

```toml
[checks.Environment.Username]
desc = "The current username"
checkEnv = "{USER}"
regex = "[a-z_][a-z0-9_-]*[$]?"
```

### checkPath

Tests the existence and type of a path.

| name      | description                                                                                                                                    |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------------------------|
| checkPath | Path to check, which may include environment varaibles wrapped in curly braces for substitution. <br>__aliases__: ``checkPath``, ``CheckPath`` |
| desc      | _(Optional)_ The description for the test                                                                                                      |
| path_type | _(Optional)_ Check whether the path corresponds to a valid ``'file'`` or ``'dir'``.                                                            |

##### Example

```toml
[checks.Environment.Pyproject]
desc = "A project's pyprojectfile"
checkPath = "./pyproject.toml"
path_type = "file"
```
