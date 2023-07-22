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

### checkEnv: Environment variables

Tests the existence and, optional, the value of an environment variable.

| name      | description                                                                                                                  |
|:----------|:-----------------------------------------------------------------------------------------------------------------------------|
| checkEnv  | Environment variable to check, wrapped in curly braces for substitution. <br>__aliases__: ``checkEnv``, ``CheckEnv``         |
| desc      | _(Optional)_ The description for the test                                                                                    |
| regex     | _(Optional)_ A regular expression to test against the environment variable value                                             |

#### Example

```toml
[checks.Environment.Username]
desc = "The current username"
checkEnv = "{USER}"
regex = "[a-z_][a-z0-9_-]*[$]?"
```
