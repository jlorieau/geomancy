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

   - Create a ``.geomancy.toml`` file with checks in the project root. See the
      ``examples`` directory for examples.

   or

   - Add the checks to a ``pyproject.toml`` file using the section heading
     ``[tool.geomancy]``.

2. Run the geo

   ```shell
   $ geo
   ```

## Format

### checkEnv: Environment variables

Tests the existence and, optional, the value of an environment variable.

__aliases__: ``checkEnv``, ``CheckEnv``

#### Required

- __value__: An environment variable name wrapped in curly braces for
  substitution

#### Optional
- __desc__: The description for the test

- __regex__: A regular expression to test against the environment variable value

#### Example

```toml
[checks.Environment.Path]
    desc = "Paths to search for executables"
    checkEnv = "{PATH}"
```
