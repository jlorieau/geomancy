.. _checkAwsSsmParameter:

checkSsmParameter
-----------------

.. automodule:: geomancy.checks.aws.ssm
    :noindex:

.. card::

    Parameters
    ^^^

    ``checkSsmParameter``: str
        | Check the AWS SSM parameter
        | *aliases*: ``checkSsmParam`` ``CheckAwsSsmParameter``, ``checkAWSSSMParameter``


    ``type``: str (Optional)
        | The type of parameter
        | *default*: `'String'`
        | *allowed values*: `'String'`, `'StringList'`, `'SecureString'`, None

    .. include:: snippets/common_args.rst

    .. include:: ../snippets/common_args.rst

.. tab-set::

    .. tab-item:: Example 1 (yaml)

        The ``checkSsmParameter`` check in YAML format.

        .. code-block:: yaml

          AWS:
            SSMParameters:
                ContainerUrl:
                  desc: The container image url
                  checkSsmParam: "/myproject/dev/containerImageUrl"

    .. tab-item:: Example 2 (toml)

        The ``checkSsmParameter`` check in TOML format.

        .. code-block:: toml

            [AWS.SSMParameters.ContainerUrl]
            desc = "The container image url"
            checkSsmParam = "/myproject/dev/containerImageUrl"

    .. tab-item:: Example 3 (toml)

        The ``checkSsmParameter`` check in abbreviated TOML format.

        .. code-block:: toml

            [AWS.SSMParameters]
            ContainerUrl = {desc = "The container image url", checkSsmParam = "/myproject/dev/containerImageUrl"}


.. versionadded:: 1.2.1
