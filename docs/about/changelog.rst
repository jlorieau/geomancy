Release Notes
#############

Versions follow `semantic versioning <https://semver.org/>`_
(``<major>.<minor>.<patch>``).

Changes in API will only be introduced in major versions with notes in the
deprecations section.

.. towncrier release notes start

`geomancy 1.0.0 <https://github.com/jlorieau/geomancy/tree/1.0.0>`_ - 2023-08-02
================================================================================

Features
--------

- `#11 <https://github.com/jlorieau/geomancy/issues/11>`_. Implemented --fixture option
- `#11 <https://github.com/jlorieau/geomancy/issues/11>`_. Implemented CheckAWSS3 for AWS buckets
- `#33 <https://github.com/jlorieau/geomancy/issues/33>`_. Implemented multi-threaded checking with concurrent.futures
- `#36 <https://github.com/jlorieau/geomancy/issues/36>`_. Added a project-wide .geomancy.yaml file


Bug Fixes
---------

- `#31 <https://github.com/jlorieau/geomancy/issues/31>`_. Fixed out-of-order rendering of check tree by implementing rich for terminal rendering


Improved Documentation
----------------------

- `#11 <https://github.com/jlorieau/geomancy/issues/11>`_. Added documentation on CheckAWSS3
- `#32 <https://github.com/jlorieau/geomancy/issues/32>`_. Implement html5 <details> and <summary> tags in the README.md features section and documentation
- `#34 <https://github.com/jlorieau/geomancy/issues/34>`_. Added API documentation


`geomancy 0.9.4 <https://github.com/jlorieau/geomancy/tree/0.9.4>`_ - 2023-07-29
================================================================================


Features
--------

- `#14 <https://github.com/jlorieau/geomancy/issues/14>`_. Added checkPlatform check for checking minimum OS versions


Improved Documentation
----------------------

- `#14 <https://github.com/jlorieau/geomancy/issues/14>`_. Added documentation for checkPlatform check


`geomancy 0.9.3 <https://github.com/jlorieau/geomancy/tree/0.9.3>`_ - 2023-07-29
================================================================================


Features
--------

- `#25 <https://github.com/jlorieau/geomancy/issues/25>`_. Implement github action to test pushes and pull requests
- `#26 <https://github.com/jlorieau/geomancy/issues/26>`_. Implemented environment.sub_env function for check values, allowing a more powerful environment variable substitution mechanism described in the docs for environment files


Improved Documentation
----------------------

- `#26 <https://github.com/jlorieau/geomancy/issues/26>`_. Updated documentation for new environment variable substitution mechanism for check values


`geomancy 0.9.2 <https://github.com/jlorieau/geomancy/tree/0.9.2>`_ - 2023-07-28
================================================================================


Features
--------

- `#6 <https://github.com/jlorieau/geomancy/issues/6>`_. Implemented CLI glob patterns for checks file arguments and env files
- `#18 <https://github.com/jlorieau/geomancy/issues/18>`_. Switched implementation of CLI in click
- `#20 <https://github.com/jlorieau/geomancy/issues/20>`_. Implement Config load_yaml, loads_yaml, dumps_yaml methods
- `#21 <https://github.com/jlorieau/geomancy/issues/21>`_. Implemented environment file loading using docker compose rules
- `#22 <https://github.com/jlorieau/geomancy/issues/22>`_. Implemented 'run' subcommand for running commands within an environment
- `#23 <https://github.com/jlorieau/geomancy/issues/23>`_. Implement ANSI color with click echo and style
- `#24 <https://github.com/jlorieau/geomancy/issues/24>`_. Implemented a simpler @env_options usage for the CLI.


Improved Documentation
----------------------

- `#6 <https://github.com/jlorieau/geomancy/issues/6>`_. Added description on file globs to running documentation
- `#21 <https://github.com/jlorieau/geomancy/issues/21>`_. Added documentation on environment file loading using docker compose rules
- `#22 <https://github.com/jlorieau/geomancy/issues/22>`_. Added documentation on the 'run' subcommand for running commands within an environment


`geomancy 0.9.1 <https://github.com/jlorieau/geomancy/tree/0.9.1>`_ - 2023-07-26
================================================================================

Improved Documentation
----------------------

- `#10 <https://github.com/jlorieau/geomancy/issues/10>`_. Added a more complete list of PyPI classifiers


`geomancy 0.9.0 <https://github.com/jlorieau/geomancy/tree/0.9.0>`_ - 2023-07-26
================================================================================

Features
--------

- `#17 <https://github.com/jlorieau/geomancy/issues/17>`_. Added YAML parsing functionality for checks files


Improved Documentation
----------------------

- `#17 <https://github.com/jlorieau/geomancy/issues/17>`_. Added YAML examples (default) in the documentation


`geomancy 0.8.1 <https://github.com/jlorieau/geomancy/tree/0.8.1>`_ - 2023-07-25
================================================================================

Features
--------

- `#9 <https://github.com/jlorieau/geomancy/issues/9>`_. Added the environment submodule and a CLI mechanism to load env files with -e/--env


Improved Documentation
----------------------

- `#7 <https://github.com/jlorieau/geomancy/issues/7>`_. Added base sphinx documentation
- `#8 <https://github.com/jlorieau/geomancy/issues/8>`_. Implement towncrier
