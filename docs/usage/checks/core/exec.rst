.. _checkExec:

checkExec
---------

.. automodule:: geomancy.checks.exec
  :noindex:

.. card::

    Parameters
    ^^^

    ``checkExec``: str
        | Executable to check. Additionally, an optional version check can be added
          with a test operator.
        | *aliases*: ``checkExec``, ``CheckExec``

    .. include:: ../snippets/common_args.rst

.. tab-set::

    .. tab-item:: Example 1 (yaml)

        The ``checkExec`` check in YAML format.

        .. code-block:: yaml

            checks:
              Ls:
                desc: List files
                checkExec: "ls"

    .. tab-item:: Example 2 (yaml)

        The ``checkExec`` check with version checking in YAML format.

        .. code-block:: yaml

            checks:
              Python:
                desc: Python interpreter (version 3.11 or higher)
                checkExec: "python3>=3.11"

    .. tab-item:: Example 3 (toml)

        The ``checkExec`` check with version checking in TOML format.

        .. code-block:: toml

            [checks.Executables.Python]
            desc = "Python interpreter (version 3.11 or higher)"
            checkExec = "python3>=3.11"

    .. tab-item:: Example 4 (toml)

        The ``checkExec`` check with version checking in abbreviated TOML format.

        .. code-block:: toml

            [checks.Executables]
            Python = { checkExec = "python3>=3.11" }
