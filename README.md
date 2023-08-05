<!-- start logo -->
<img src="https://raw.githubusercontent.com/jlorieau/geomancy/main/docs/_static/geomancy_logo.svg" alt="geomancy logo" height="150px"/>
<!-- end logo -->

<!-- start badges -->
[![pypi version](https://img.shields.io/pypi/v/geomancy.svg)](https://pypi.org/project/geomancy/)
[![python versions](https://img.shields.io/pypi/pyversions/geomancy.svg)](https://pypi.org/project/geomancy/)
[![Black formatting](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Documentation Status](https://readthedocs.org/projects/geomancy/badge/?version=latest)](https://geomancy.readthedocs.io/en/latest/?badge=latest)
<!-- end badges -->
<!-- start intro -->
Geomancy makes it easy to check and validate environments, such as development,
testing and production.

Environment checks and tests are helpful for testing the correct setting
of environment variables, the installation and versions of installed
executables, the state of external dependencies, like LaTeX packages, or cloud
resources, or for checking environments that use the
[12-factor](http://12factor.net/) principles.
<!-- end intro -->

## Features

<!-- start features -->

### Capabilities

<p>
<details>
<summary>
<strong><u>Validation of layered and combined environments</u></strong>
</summary>

Layered environments could include a _common_ or _base_ environment, with
additional checks for settings of _test_, _development_ and _production_
environments.

In the following checks file, the existence of an environment file and a secrets
file can be checked based on the ``$ENV`` environment variable. (See the
[docker environment variable parameter expansion rules](https://docs.docker.com/compose/environment-variables/env-file/#parameter-expansion))

```yaml
checks:
  Environment:
    desc: Check environment variables in different deployments

    CheckEnvFile:
      desc: Check the existence of the environment file
      checkPath: "deployments/${ENV}/.env"

    CheckSecretsFile:
      desc: Check the existence of the secrets file
      checkPath: "deployments/${ENV}/.secrets"
```

This check file can be used to check multiple environments:

```shell
# check "dev" environment
$ geo -e deployments/base/.env -e deployments/dev/.env checks.yaml
...
# check "test" environment
$ geo -e deployments/base/.env -e deployments/test/.env checks.yaml
...
```
In this case, ``deployments/dev/.env`` is an
[environment file](https://docs.docker.com/compose/environment-variables/env-file/)
that sets ``ENV=dev``, ``deployments/test/.env`` is an
[environment file](https://docs.docker.com/compose/environment-variables/env-file/)
that sets ``ENV=test``.
</details>
</p>

<p>
<details>
<summary>
<strong><u>Full environment file support</u></strong> of the docker
<a href="https://docs.docker.com/compose/environment-variables/env-file/">env file syntax</a>
</summary>

Environment files are loaded using the ``-e/--env`` option,
which can be layered for different environments.

```shell
# Run checks for 'dev' environment
$ geo -e deployments/base/.env -e deployments/dev/.env check
...
# Run checks for 'test' environment
$ geo -e base.env -e test.env run -- echo "Test environment"
```
</details>
</p>

<p>
<details>
<summary>
<strong><u>Concurrent checks with multiple threads</u></strong> to quickly probe
I/O bound resources
</summary>

The following example concurrently checks that the 3 AWS S3 buckets are
accessible using the
[current credentials](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html)
and are secured.

This example is in yaml format, and checks can be formatted in toml format
as well.

```yaml
AWS:
  TemplateS3:
    checkS3: myproject-cfn-templates
  StaticS3:
    checkS3: myproject-static
  MediaS3:
    checkS3: myproject-media

```
</details>
</p>

<p>
<details>
<summary>
<strong><u>Load checks in multiple formats</u></strong>
</summary>

Including [yaml](https://yaml.org) (e.g. ``.geomancy.yaml``)

```yaml
checks:
  Environment:
    desc: Check environment variables common to all development environments

    Path:
      decs: Paths to search for executables
      checkEnv: $PATH
```

or [toml](https://toml.io/en/) (e.g. ``.geomancy.toml``)

```toml
[checks.Environment]
desc = "Check environment variables common to all development environments"

    [checks.Environment.Path]
    desc = "Paths to search for executables"
    checkEnv = "$PATH"
```

or [pyproject.toml](https://peps.python.org/pep-0621/)

```toml
[tool.geomancy.checks.Environment]
desc = "Check environment variables common to all development environments"

    [tool.geomancy.checks.Environment.Path]
    desc = "Paths to search for executables"
    checkEnv = "$PATH"
```

</details>
</p>

### Available Checks

<p>
<details>
<summary><strong><u>Operating systems</u></strong> meet the minimum required
  versions
  (<a href="https://geomancy.readthedocs.io/en/latest/usage/format.html#checkplatform">checkOS</a>)
</summary>

The following shows an example in yaml format. Checks can be formatted in
toml format as well.

```yaml
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
</details>
</p>

<p>
<details>
<summary><strong><u>Environment variables</u></strong> are properly set and
  have valid values with regular expressions
  (<a href="https://geomancy.readthedocs.io/en/latest/usage/format.html#checkenv">checkEnv</a>)
</summary>

The following shows an example in yaml format. Checks can be formatted in
toml format as well.

```yaml
Username:
  desc: The current username
  checkEnv: "$USER"
  regex: "[a-z_][a-z0-9_-]*[$]?"
```
</details>
</p>

<p>
<details>
<summary><strong><u>Paths</u></strong> exist and they're the right type
  (<a href="https://geomancy.readthedocs.io/en/latest/usage/format.html#checkpath">checkPath</a>)
</summary>

The following shows an example in yaml format. Checks can be formatted in
toml format as well.

```yaml
PyprojectToml:
  desc: A project's pyprojectfile
  checkPath: ./pyproject.toml
  type: file
```
</details>
</p>

<p>
<details>
<summary><strong><u>Executables</u></strong> are available and meet minimum
  or correct versions
  (<a href="https://geomancy.readthedocs.io/en/latest/usage/format.html#checkexec">checkExec</a>)
</summary>

The following shows an example in yaml format. Checks can be formatted in
toml format as well.

```yaml
Python:
  desc: Python interpreter (version 3.11 or higher)
  checkExec: "python3>=3.11"
```
</details>
</p>

<p>
<details>
<summary><strong><u>Python packages</u></strong> are available minimum or
  correct versions
  (<a href="https://geomancy.readthedocs.io/en/latest/usage/format.html#checkpythonpkg">checkPythonPkg</a>)
</summary>

The following shows an example in yaml format. Checks can be formatted in
toml format as well.

```yaml
PythonPackages:
  geomancy:
    desc: Geomancy python package
    checkPythonPkg: "geomancy>=0.1"
```
</details>
</p>

<p>
<details>
<summary><strong><u>Group checks</u></strong> and specify
  conditional (all or any) pass criteria
  (<a href="https://geomancy.readthedocs.io/en/latest/usage/format.html#check-groups">Groups of Checks</a>)
</summary>

The following shows an example with the ``checks`` group containing 2 groups,
``OperatingSystem``, ``Environment``.

The ``OperatingSystem`` group contains 3 checks: ``checkMacOS``,
``checkLinuxOS``, ``checkWindows``, and the ``OperatingSystem`` group check
passes if any of these 3 checks pass (``subchecks: any``)

The ``Environment`` group contains 1 check, ``Path``, and 1 group, ``Username``,
which itself contains 2 checks: ``UnixUsername`` and ``WindowsUsername``.

This example is in yaml format, and checks can be formatted in toml format
as well.

```yaml
checks:
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

  Environment:
    desc: Check environment variables common to all development environments

    Path:
      decs: Paths to search for executables
      checkEnv: $PATH
    Username:
      subchecks: any

      UnixUsername:  # Username on linux and macOS
        desc: The current username
        checkEnv: $USER
        regex: "[a-z_][a-z0-9_-]*[$]?"
      WindowsUsername:  # Username on Windows
        desc: The current username
        checkEnv: $USERNAME
        regex: "[a-z_][a-z0-9_-]*[$]?"

```
</details>
</p>

<p>
<details>
<summary><strong><u>AWS</u></strong> resources exist and are securely setup
  (<a href="https://geomancy.readthedocs.io/en/latest/usage/checks/aws/index.html">AWS checks</a>)
</summary>

The following shows an example in yaml format. Checks can be formatted in
toml format as well.

```yaml
AWS:
  IAM:
    desc: Check the default authentication and security settings
    checkIAM:

  TemplatesS3Bucket:
    desc: Check the bucket for cloudformation templates
    checkS3: "myproject-cfn-templates"
```
</details>
</p>

<!-- end features -->

## Quickstart
<!-- start quickstart -->
1. Create a ``.geomancy.yaml`` file with checks. See
   [examples/geomancy.yaml](https://github.com/jlorieau/geomancy/blob/main/examples/geomancy.yaml)
   for an example of all checks.

    ```yaml
    Environment:
      desc: Check environment variables common to all development environments

      Username:
        desc: The current username
        checkEnv: "$USER"
        regex: "[a-z_][a-z0-9_-]*[$]?"

    Paths:
      desc: Checks the existence of needed files and directories
      subchecks: "any" # at least one of the files must be present

      Geomancy:
        desc: Check for the 'geomancy.toml' file
        checkPath: examples/geomancy.toml
        type: file
      Pyproject:
        desc: Check for 'pyproject.toml' file
        checkPath: examples/pyproject.toml
        type: file

    Executables:
      desc: Check the availability of commands and their versions

      Python:
        desc: Python interpreter ver 3.11 or higher
        checkExec: python3>=3.11
    ```

2. Use ``geo`` to run the checks.

    ```shell
     [✔] test.yaml...passed
     [✔]   Environment...passed
     [✔]     Check environment variable '$USER'...passed
     [✔]   Paths...passed
     [✔]     Check path 'examples/geomancy.toml'...passed
     [✔]     Check path 'examples/pyproject.toml'...passed
     [✔]   Executables...passed
     [✔]     Check executable 'python3>=3.11'...passed
    ================================= 8 passed in 0.50s ==================================
    ```

    (By default, ``geomancy`` will search ``.geomancy.y[a]ml``, ``geomancy.y[a]ml``
    ``.geomancy.toml``, ``geomancy.toml`` and ``pyproject.toml``.)
<!-- end quickstart -->


## Documentation

For full documentation please see https://geomancy.readthedocs.io/en/latest.


## Bugs or Requests
Please use the [GitHub issue tracker](https://github.com/jlorieau/geomancy/issues)
to submit bugs or request features.

## Similar projects

The following projects share some of the same goals in different contexts:

- [Envalid](https://github.com/af/envalid)
- [AWS Config](https://aws.amazon.com/config/)

## License

Copyright Justin Lorieau and others, 2023.

Distributed under the terms of the [MIT license](LICENSE).
geomancy is free and open source software.
