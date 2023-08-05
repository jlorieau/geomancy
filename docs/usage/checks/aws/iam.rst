.. _checkAwsIam:

checkAwsIam
-----------

.. automodule:: geomancy.checks.aws.iam
  :noindex:

.. card::

    Parameters
    ^^^

    ``checkAwsIam``:
        | Check the IAM account
        | *aliases*: ``checkIAM``, ``CheckIAM``, ``checkAWSIAM``, ``checkAwsIAM``,
          ``CheckAwsIAM``,

    ``root``: bool (Optional)
        | Security check for root access key and signing certificate availability
        | *aliases*: ``root_access``
        | *default*: True

    ``age``: int (Optional)
        | Security check the age of access and secret keys (in days)
        | *aliases*: ``key_age``
        | *default*: 90

    .. include:: snippets/common_args.rst

    .. include:: ../snippets/common_args.rst

.. tab-set::

    .. tab-item:: Example 1 (yaml)

        The ``checkAwsIam`` check in YAML format.

        .. code-block:: yaml

            checks:
              IAM:
                desc: "Check IAM authentication and security settings"
                checkIAM:

    .. tab-item:: Example 2 (toml)

        The ``checkAwsIam`` check in TOML format.

        .. code-block:: toml

            [checks.Iam]
            desc = "Check IAM authentication and security settings"
            chekIAM = ""
