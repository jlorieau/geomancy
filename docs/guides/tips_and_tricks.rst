.. _tips-and-tricks:

Tips and Tricks
===============

Unwanted environment substitution
---------------------------------

Environment variables, denoted by strings starting with a ``$`` character, are
substituted by default in the values passed to checks. This can be avoided by
setting ``substitute`` to False or by using a literal with single quotes.

.. tab-set::

    .. tab-item:: substitute (yaml)

        .. code-block:: yaml

            MyOddFilename:
              checkPath: myfile$.txt
              substitute: False

    .. tab-item:: literal string (yaml)

        Use triple (3) single quotes

        .. code-block:: yaml

            MyOddFilename:
              checkPath: '''myfile$.txt'''

    .. tab-item:: substitute (toml)

        .. code-block:: toml

            [MyOddFilename]
            checkpath='myfile$.txt'
            substitute=false

    .. tab-item:: literal string (toml)

        Use quadruple (4) single quotes

        .. code-block:: toml

            [MyOddFilename]
            checkpath=''''myfile$.txt''''

Flat Checks Files
-----------------

Checks can be conveniently grouped by category, but this is not a strict
requirement for checks files. The following show file format examples
with checks at the root level, with an example on putting each check on 1 line.

.. tab-set::

    .. tab-item:: example 1 (yaml)

        .. code-block:: yaml

            Geomancy:
              desc: Check for the 'geomancy.toml' file
              checkPath: examples/geomancy.toml
              type: file

            Pyproject:
              desc: Check for 'pyproject.toml' file
              checkPath: examples/pyproject.toml
              type: file

    .. tab-item:: example 2 (toml)

        .. code-block:: toml

            [Geomancy]
            desc = "Check for the 'geomancy.toml' file"
            checkPath = "examples/geomancy.toml"
            type = "file"

            [Pyproject]
            desc = "Check for 'pyproject.toml' file"
            checkPath = "examples/pyproject.toml"
            type = "file"

    .. tab-item:: example 3 (toml, 1 line)

        .. code-block:: toml

            Geomancy = {checkPath = "examples/geomancy.toml", type = "file"}
            Pyproject = {checkPath = "examples/pyproject.toml", type = "file"}
