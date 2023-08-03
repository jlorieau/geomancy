.. _checkEnv:

checkEnv
--------

.. automodule:: geomancy.checks.env
  :noindex:

.. card::

    Parameters
    ^^^

    ``checkEnv``: str
        | Environment variable to check, wrapped in curly braces for substitution
        | *aliases*: ``checkEnv``, ``CheckEnv``

    ``regex``: str (Optional)
        | A regular expression to check against the environment variable value

    .. include:: ../snippets/common_args.rst

.. tab-set::

    .. tab-item:: Example 1 (yaml)

        The ``checkEnv`` check in YAML format.

        .. code-block:: yaml

            checks:
              Environment:
                Username:
                  desc: The current username
                  checkEnv: "$USER"
                  regex: "[a-z_][a-z0-9_-]*[$]?"

    .. tab-item:: Example 2 (toml)

        The ``checkEnv`` check in TOML format.

        .. code-block:: toml

            [checks.Environment.Username]
            desc = "The current username"
            checkEnv = "$USER"
            regex = "[a-z_][a-z0-9_-]*[$]?"

    .. tab-item:: Example 3 (toml)

        The ``checkEnv`` check in abbreviated TOML format.

        .. code-block:: toml

            [checks.Environment]
            Username = {checkEnv = "{USER}", regex = "[a-z_][a-z0-9_-]*[$]?"}
