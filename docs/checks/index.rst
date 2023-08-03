Checks
======

The following is a listing of available checks in geomancy.

Core
----

Core checks are always available and do not have additional requirements.

:ref:`check`
    .. automodule:: geomancy.checks.base
        :noindex:

:ref:`checkEnv`
    .. automodule:: geomancy.checks.env
        :noindex:

:ref:`checkExec`
    .. automodule:: geomancy.checks.exec
        :noindex:

:ref:`checkPath`
    .. automodule:: geomancy.checks.path
        :noindex:

:ref:`checkPlatform`
    .. automodule:: geomancy.checks.platform
        :noindex:

:ref:`checkPythonPkg`
    .. automodule:: geomancy.checks.python
        :noindex:

AWS
---

Checks for Amazon Web Service (`AWS <https://aws.amazon.com>`_) resources:

:ref:`checkAwsS3`
    .. automodule:: geomancy.checks.aws.s3
        :noindex:


.. warning::

    Amazon Web Service (`AWS <https://aws.amazon.com>`_) checks require the
    installation of aws dependencies.

    .. code-block:: shell

        # Install the 'aws' dependency
        $ python -m pip install geomancy[aws]
        # Install 'all' dependencies
        $ python -m pip install geomancy[all]


.. versionchanged:: 0.9.3
    Environment variables are now referenced by the name preceded by a ``$`` and
    optional braces. e.g. ``$USER`` or ``${USER}``

.. toctree::
    :caption: core
    :maxdepth: 2
    :glob:
    :hidden:

    core/*

.. toctree::
    :caption: aws
    :maxdepth: 2
    :glob:
    :hidden:

    aws/*
