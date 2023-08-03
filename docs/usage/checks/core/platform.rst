.. _checkPlatform:

checkPlatform
-------------

.. automodule:: geomancy.checks.platform
  :noindex:

.. card::

    Parameters
    ^^^

    ``checkPlatform``: str
        | Operating system to check. Additionally, an optional version check can be added
          with a test operator
        | *aliases*: ``checkOS``, ``checkPlatform``

    .. include:: ../snippets/common_args.rst

.. tab-set::

    .. tab-item:: Example 1 (yaml)

        The ``checkPlatform`` check in YAML format.

        .. code-block:: yaml

            check:
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

    .. tab-item:: Example 2 (toml)

        The ``checkPlatform`` check in TOML format.

        .. code-block:: toml

            [checks.OperatingSystem]
            desc = "Check the minimum operating system versions"
            subchecks = "any"

                [checks.OperatingSystem.checkMacOS]
                desc = "MacOS 10.9 or later (released 2013)"
                checkOS = "macOS >= 10.9"

                [checks.OperatingSystem.checkLinuxOS]
                desc = "Linux 4.0 or later (released 2015)"
                checkOS = "Linux >= 3.0"

                [checks.OperatingSystem.checkWindows]
                desc = "Windows 10 or later (released 2015)"
                checkOS = "Windows >= 10"

    .. tab-item:: Example 3 (toml)

        The ``checkPlatform`` check in abbreviated TOML format.

        .. code-block:: toml

            [checks.OperatingSystem]
            desc = "Check the minimum operating system versions"
            subchecks = "any"

            checkMacOS = {desc = "MacOS 10.9 or later (released 2013)", checkOS = "macOS >= 10.9"}
            checkLinuxOS = {desc = "Linux 4.0 or later (released 2015)", checkOS = "Linux >= 3.0"}
            checkWindows = {desc = "Windows 10 or later (released 2015)", checkOS = "Windows >= 10"}
