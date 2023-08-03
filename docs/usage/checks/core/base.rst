.. _check:

Checks and Groups
-----------------

.. automodule:: geomancy.checks.python
  :noindex:

.. card::

    Parameters
    ^^^

    ``desc``: str (Optional)
        | The description for the check group

    ``subchecks``: str (Optional)
        | The pass condition for the sub-checks of the group. Can be either ``'all'``
          to require that all sub-checks pass or ``'any'`` to require that only one
          sub-check passes.
        | *default*: ``'all'``
        | *aliases*: ``condition``

.. tab-set::

    .. tab-item:: Example 1 (yaml)

        The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
        ``Pyproject``.

        .. code-block:: yaml

            checksFiles:
              desc: Checks that at least one checks file exists
              subchecks: any

              Geomancy:
                desc: Check for the 'geomancy.toml' file
                checkPath: examples/geomancy.toml
                type: file
              Pyproject:
                desc: Check for 'pyproject.toml' file
                checkPath: examples/pyproject.toml
                type: file

    .. tab-item:: Example 2 (toml)

        The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
        ``Pyproject``.

        .. code-block:: toml

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

    .. tab-item:: Example 3 (toml)

        The following is a check group ``ChecksFile`` with 2 checks, ``Geomancy`` and
        ``Pyproject``, in abbreviated format.

        .. code-block:: toml

            [checks.ChecksFile]
            subchecks = "any"

            Geomancy = { checkPath = "examples/geomancy.toml", type = "file" }
            Pyproject = { checkPath = "examples/pyproject.toml", type = "file" }
