.. _checkPythonPkg:

checkPythonPkg
--------------

.. automodule:: geomancy.checks.python
  :noindex:

.. card::

    Parameters
    ^^^

    ``checkPythonPkg``: str
        | Python package to check. Additionally, an optional version check can be added
          with a test operator.
        | *aliases*: ``checkPythonPkg``, ``CheckPythonPkg``, ``checkPythonPackage``,
          ``CheckPythonPackage``

    .. include:: ../snippets/common_args.rst

.. tab-set::

    .. tab-item:: Example 1 (yaml)

        The ``checkPythonPkg`` check in YAML format.

        .. code-block:: yaml

            checks:
              PythonPackages:
                geomancy:
                  desc: Geomancy python package
                  checkPythonPkg: "geomancy>=0.1"

    .. tab-item:: Examples 2 (toml)

        The ``checkPythonPkg`` check in TOML format.

        .. code-block:: toml

            [checks.PythonPackages.geomancy]
            desc = "Geomancy python package"
            checkPythonPkg = "geomancy>=0.1"

    .. tab-item:: Example 3 (toml)

        The ``checkPythonPkg`` check in abbreviated TOML format.

        .. code-block:: toml

            [checks.PythonPackages]
            geomancy = { checkPythonPkg = "geomancy>=0.1" }
