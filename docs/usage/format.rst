.. _file-format:

Checks Files
============

The checks file is formatted in `yaml <https://yaml.org>`_ or
`toml <https://toml.io/en/>`, and it contains a listing of checks and,
optionally, configuration options for geomancy.

Filenames
---------

The checks file may be a dedicated file for geomancy, such as a
``.geomancy.yaml`` or ``.geomancy.toml`` file in the project root
directory, or it may be incorporated as part of a ``pyproject.toml`` file
under the ``[tool.geomancy]`` section.

.. tab-set::

    .. tab-item:: geomancy.yaml

        .. code-block:: yaml

            checks:
              Username:
                desc: The current username
                checkEnv: "$USER"
                regex: "[a-z_][a-z0-9_-]*[$]?"

    .. tab-item:: geomancy.toml

        .. code-block:: toml

            [checks.Username]
            desc = "The current username"
            checkEnv = "$USER"
            regex = "[a-z_][a-z0-9_-]*[$]?"

    .. tab-item:: pyproject.toml

        .. code-block:: toml

            [tool.geomancy.checks.Username]
            desc = "The current username"
            checkEnv = "$USER"
            regex = "[a-z_][a-z0-9_-]*[$]?"


Nesting and Listing Checks
--------------------------

Checks can be grouped into sections of related checks, and the pass condition
for child checks can be customized.

.. tab-set::

    .. tab-item:: geomancy.yaml

        By default, all child checks must pass for the parent check to pass.
        In this example, the parent check, ``ChecksFile``, may pass if any of the
        3 child checks pass--either ``GeomancyToml``, ``PyprojectToml`` or
        ``GeomancyYaml``. This condition is specified by ``subchecks = any`` option.

        .. code-block:: yaml

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

    .. tab-item:: geomancy.toml


        By default, all child checks must pass for the parent check to pass.
        In this example, the parent check, ``ChecksFile``, may pass if any of the
        3 child checks pass--either ``GeomancyToml``, ``PyprojectToml`` or
        ``GeomancyYaml``. This condition is specified by ``subchecks = "any"`` option.

        .. code-block:: toml

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

    .. tab-item:: pyproject.toml

        By default, all child checks must pass for the parent check to pass.
        In this example, the parent check, ``ChecksFile``, may pass if any of the
        3 child checks pass--either ``GeomancyToml``, ``PyprojectToml`` or
        ``GeomancyYaml``. This condition is specified by ``subchecks = "any"`` option.

        .. code-block:: toml

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


Configuration
-------------

Checks files may optionally include configuration settings for geomancy. The
[config](#configuration) lists the current default configuration.

.. tab-set::

    .. tab-item:: geomancy.yaml

        Configuration settings are specified the ``config`` section.

        .. code-block:: yaml

            config:
              CHECKBASE:
                ENV_SUBSTITUTE_DEFAULT: true

    .. tab-item:: geomancy.toml

        Configuration settings are specified the ``[config]`` section.

        .. code-block:: toml

            [config]
            [config.CHECKBASE]
            ENV_SUBSTITUTE_DEFAULT = true

    .. tab-item:: pyproject.toml

        Configuration settings are specified in the ``[tool.geomancy.config]`` section.

        .. code-block:: toml

            [tool.geomancy.config]
            [tool.geomancy.config.CHECKBASE]
            ENV_SUBSTITUTE_DEFAULT = true
