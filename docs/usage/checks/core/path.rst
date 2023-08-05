.. _checkPath:

checkPath
---------

.. automodule:: geomancy.checks.path
  :noindex:

.. card::

    Parameters
    ^^^

    ``checkPath``: str
        | Path to check, which may include environment variables for substitution
        | *aliases*: ``checkPath``, ``CheckPath``

    ``type``: str (Optional)
        Additionally check whether the path corresponds to a valid ``'file'`` or
        ``'dir'``.

    .. include:: ../snippets/common_args.rst

.. tab-set::

    .. tab-item:: Example 1 (yaml)

        The ``checkPath`` check in YAML format.

        .. code-block:: yaml

            checks:
              Pyproject:
                desc: A project's pyprojectfile
                checkPath: ./pyproject.toml
                type: file

    .. tab-item:: Example 2 (toml)

        The ``checkPath`` check in TOML format.

        .. code-block:: toml

            [checks.Environment.Pyproject]
            desc = "A project's pyprojectfile"
            checkPath = "./pyproject.toml"
            type = "file"

    .. tab-item:: Example 3 (toml)

        The ``checkPath`` check in abbreviated TOML format.

        .. code-block:: toml

            [checks.Environment]
            Pyproject = { checkPath = "./pyproject.toml", type = "file" }
