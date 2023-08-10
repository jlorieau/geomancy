AWS
---

Checks for Amazon Web Service (`AWS <https://aws.amazon.com>`_) resources:

:ref:`checkAwsIam`
    .. automodule:: geomancy.checks.aws.iam
        :noindex:

:ref:`checkAwsS3`
    .. automodule:: geomancy.checks.aws.s3
        :noindex:

:ref:`checkAwsSsmParameter`
    .. automodule:: geomancy.checks.aws.ssm
        :noindex:

.. warning::

    Amazon Web Service (`AWS <https://aws.amazon.com>`_) checks require the
    installation of aws dependencies.

    .. code-block:: shell

        # Install the 'aws' dependency
        $ python -m pip install geomancy[aws]
        # Install 'all' dependencies
        $ python -m pip install geomancy[all]

.. toctree::
    :hidden:
    :maxdepth: 1
    :glob:

    *
