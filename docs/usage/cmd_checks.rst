.. _running-checks:

Running Checks
==============

Specifying Checks to Run
------------------------

Geomancy can find checks from files in pre-defined locations, if file
arguments aren't specified, or it can run checks from the files specified as
arguments.

The format of the checks file is specified in the :ref:`file-format`.

.. tab-set::

    .. tab-item:: without arguments

        When no arguments are specified, geo will search for checks in multiple
        locations.

        .. code-block:: shell

            $ geo
             [✔] examples/geomancy.yaml...passed
             [✔]   checks...passed
             [✔]     OperatingSystem...passed
             [✔]       Check platform 'macOS >= 10.9'...passed
             [!]       Check platform 'Linux >= 3.0'...wrong platform
             [!]       Check platform 'Windows >= 10'...wrong platform
             [✔]     Environment...passed
             [✔]       Check environment variable '$PATH'...passed
             [✔]       Username...passed
             [✔]         Check environment variable '$USER'...passed
             [!]         Check environment variable '$USERNAME'...empty string
             [✔]     Paths...passed
             [✔]       ChecksFile...passed
             [✔]         Check path 'examples/geomancy.toml'...passed
             [✔]         Check path 'examples/pyproject.toml'...passed
             [!]         Check path '.missing__.txt'...missing
             [✔]     Executables...passed
             [✔]       Check executable 'python3>=3.11'...passed
             [✔]     PythonPackages...passed
             [✔]       Check python package 'geomancy>=0.8'...passed

    .. tab-item:: with arguments

        The following evaluates the checks listed in ``examples/geomancy.yaml``, if
        this file exists.

        .. code-block:: shell

            $ geo examples/geomancy.yaml
             [✔] examples/geomancy.yaml...passed
             [✔]   checks...passed
             [✔]     OperatingSystem...passed
             [✔]       Check platform 'macOS >= 10.9'...passed
             [!]       Check platform 'Linux >= 3.0'...wrong platform
             [!]       Check platform 'Windows >= 10'...wrong platform
             [✔]     Environment...passed
             [✔]       Check environment variable '$PATH'...passed
             [✔]       Username...passed
             [✔]         Check environment variable '$USER'...passed
             [!]         Check environment variable '$USERNAME'...empty string
             [✔]     Paths...passed
             [✔]       ChecksFile...passed
             [✔]         Check path 'examples/geomancy.toml'...passed
             [✔]         Check path 'examples/pyproject.toml'...passed
             [!]         Check path '.missing__.txt'...missing
             [✔]     Executables...passed
             [✔]       Check executable 'python3>=3.11'...passed
             [✔]     PythonPackages...passed
             [✔]       Check python package 'geomancy>=0.8'...passed

If no checks files are listed as arguments, geo will search the following file
locations in the current directory, and it wil run all the checks in existing
files: ``.geomancy.yaml``, ``.geomancy.yml``, ``.geomancy.toml``,
``geomancy.yaml``, ``geomancy.yml``, ``geomancy.toml``, ``pyproject.toml``

.. admonition:: Layering and combining checks
    :class: tip

    Multiple checks files can be run together allowing the mixing and matching
    of test sets.

    For example, a ``dev`` environment and ``prod`` environment may have common
    checks, listed in ``base.yaml``, in addition to environment specific checks
    listed in ``dev.yaml`` and ``prod.yaml`` respectively.

    .. code-block:: shell

        $ geo base.yaml dev.yaml   # 'dev' environment
        ...
        $ geo base.yaml prod.yaml  # 'prod environment
        ...

.. admonition:: Wildcards and glob patterns
    :class: tip

    The check file arguments support wildcards and glob patterns to run checks
    from multiple files at once. For example, the following will run checks in
    all files that have the ``geomancy`` filename: ``$ geo geomancy.*``


.. _configuration:

Configuration
-------------

As described in the :ref:`file-format` section, configuration options are
placed in the ``config`` section of checks files or the
``[tool.geomancy.config]`` section of the ``pyproject.toml`` file.

The default configuration options can be listed in `yaml <http://yaml.org>`_
or `toml <https://toml.io/en>`_ formats.

.. tab-set::

    .. tab-item:: config (yaml)

        .. code-block:: shell

            $ geo config --yaml
            config:
              CHECKBASE:
                ENV_SUBSTITUTE_DEFAULT: true
                MAX_LEVEL: 10
            ...

    .. tab-item:: config (toml)

        .. code-block:: shell

            $ geo config ---toml
            [config]
            VERSION='0.9.2'

              [config.CHECKBASE]
              ENV_SUBSTITUTE_DEFAULT=true
              MAX_LEVEL=10...
            ...


.. _environment-files:

Environment Variables and Files
-------------------------------

Environment variables can be loaded from one or more environment files
(a.k.a dotenv files) with the ``-e``/``--env`` flag.

.. code-block:: shell

    $ geo -e .base.env -e .dev.env


By default, existing environment variables, or environment variables set
by preceding env files, are not overwritten. To change this behavior,
use the ``--overwrite`` flag.

.. code-block:: shell

    $ geo -e .base.env -e .dev.env --overwrite

.. admonition:: Layering and combining environments
    :class: tip

    Layered environments can be created by splitting environment variables
    between multiple environment files and invoking the ``-e``/``--env`` flag
    multiple times. For example, a ``.base.env`` file could contain environment
    variables common to all environments, while a ``.dev.env`` file could
    contain environment variables for the 'dev' environment.

.. admonition:: Geomancy within environments
    :class: attention

    Even though geomancy supports the loading of environment files, it is
    recommended that environments are validated using the environment file
    loading mechanism used in practice.

    For example, if an environment file is used within
    `docker compose <https://docs.docker.com/compose/>`_, the geomancy checks
    should be tested within the docker compose container.

.. _environment-files-syntax:

Syntax
^^^^^^

Environment files are a superset of the
`docker compose environment file syntax <https://docs.docker.com/compose/environment-variables/env-file/#syntax>`_.
Specifically,

#.  Environment variable names may contain letters (``A-Z`` or ``a-z``),
    numbers (``0-9``) and underscores (``_``), but the first character must be a
    letter (``A-Z`` or ``a-z``)

#.  Lines beginning with a ``#`` are considered a comment and ignored

#.  Blank lines are ignored

#.  Each line represents an environment variable name-value pair. Values may
    be quoted.

    .. code-block:: shell

        VAR=VAL    # -> VAL
        VAR="VAL"  # -> VAL
        VAR='VAL'  # -> VAL

#.  Inline comments must be preceded by a space

    .. code-block:: shell

       VAR=VALUE # comment       # -> VALUE
       VAR=VALUE# not a comment  # -> VALUE# not a comment

#.  Comments for quoted values must follow the quote

    .. code-block:: shell

        VAR="VALUE # not a comment"  # -> VALUE # not a comment
        VAR="VALUE"  # comment       # -> VALUE


#.  Single-quoted values are taken literally

    .. code-block:: shell

        VAR='$OTHER'    # -> $OTHER
        VAR='${OTHER}'  # -> ${OTHER}

#.  Quotes can be escaped

    .. code-block:: shell

        VAR='Let\'s go!'             # -> Let's go!
        VAR="{\"hello\": \"json\"}"  # -> {"hello": "json"}

#.  Shell escape sequences (``\n``, ``\t``, ``\r``, ``\\``) are supported in
    double-quoted values

    .. code-block:: shell

        VAR="some\tvalue"  # -> some    value
        VAR='some\tvalue'  # -> some\tvalue
        VAR=some\tvalue     # -> some\tvalue

#.  Environment file values are substituted according to the
    :ref:`substitution <environment-substitution>` rules.

    .. code-block:: shell

        MYVAR=MYVALUE
        VAR1=$MYVAR      # VAR1=MYVALUE

.. _environment-substitution:

Substitution
^^^^^^^^^^^^

The following rules follow the
`docker compose environment substitution syntax <https://docs.docker.com/compose/environment-variables/env-file/#syntax>`_
for substituting environment variables in values.

#.  Environment variables are substituted when preceded by a ``$`` and may or
    may not contain braces. e.g. ``$USER`` or ``${USER}``

#.  **Direct substitution** of braced (``${VAR}``) and unbraced (``$VAR``)
    variables may be done in unquoted or double-quoted values--not single-quoted
    literals.

    .. code-block:: shell

        MYVAR=MYVALUE
        $MYVAR      # -> MYVALUE
        "${MYVAR}"  # -> MYVALUE
        '${MYVAR}'  # -> ${MYVAR}

#.  **Default value substitution** will return the default value if the variable
    isn't set or is empty. Defaults can contain spaces in the braced version,
    but not quotes.

    .. code-block:: shell

        ${MISSING-my default value}   # -> my default value
        ${MISSING:-my default value}  # -> my default value
        $MISSING-default              # -> default
        $MISSING:-default             # -> default

#.  **Error value substitution** will raise an exception with the given error
    message if an environment variable isn't set or is empty. Errors can contain
    spaces in the braced version, but not quotes

    .. code-block:: shell

        ${MISSING?no value}   # -> raises EnvironmentError("no value")
        ${MISSING:?no value}  # -> raises EnvironmentError("no value")
        $MISSING?missing      # -> raises EnvironmentError("missing")
        $MISSING:?missing     # -> raises EnvironmentError("missing")

#.  **Replacement value substitution** will replace a set environment variable
    with the replacement value, otherwise it will produce an empty string.
    Replacements can contain spaces in the braced version, but not quotes

    .. code-block:: shell

        MYVAR=MYVALUE
        ${MYVAR+replaced}   # -> replaced
        ${MYVAR:+replaced}  # -> replaced
        $MYVAR+replaced     # -> replaced
        $MYVAR:+replaced    # -> replaced
        ${MISSING+replaced} # ""
        ${MISSING+replaced} # ""

Other Options
-------------

The following are options available to ``geo`` and``geo check``.

``-e``/``--env``
    Environment variable file(s) to load for checks

``--overwrite``
    Overwrite existing environment variables with those listed in environment
    variable files. This option requires environment variable files to be
    specified with `-e`/`--env`
