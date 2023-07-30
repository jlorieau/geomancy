# Changelog

Versions follow [semantic versioning](https://semver.org/>)
(``<major>.<minor>.<patch>``).

Changes in API will only be introduced in major versions with notes in the
deprecations section.

% Do not edit below this line, as the changelog is managed by towncrier

<!-- towncrier release notes start -->

## [0.9.4](https://github.com/jlorieau/geomancy/tree/0.9.4) - 2023-07-29


### Features

- [#14](https://github.com/jlorieau/geomancy/issues/14). Added checkPlatform check for checking minimum OS versions


### Improved Documentation

- [#14](https://github.com/jlorieau/geomancy/issues/14). Added documentation for checkPlatform check


## [0.9.3](https://github.com/jlorieau/geomancy/tree/0.9.3) - 2023-07-29


### Features

- [#25](https://github.com/jlorieau/geomancy/issues/25). Implement github action to test pushes and pull requests
- [#26](https://github.com/jlorieau/geomancy/issues/26). Implemented environment.sub_env function for check values, allowing a more powerful environment variable substitution mechanism described in the docs for environment files


### Improved Documentation

- [#26](https://github.com/jlorieau/geomancy/issues/26). Updated documentation for new environment variable substitution mechanism for check values


## [0.9.2](https://github.com/jlorieau/geomancy/tree/0.9.2) - 2023-07-28


### Features

- [#6](https://github.com/jlorieau/geomancy/issues/6). Implemented CLI glob patterns for checks file arguments and env files
- [#18](https://github.com/jlorieau/geomancy/issues/18). Switched implementation of CLI in click
- [#20](https://github.com/jlorieau/geomancy/issues/20). Implement Config load_yaml, loads_yaml, dumps_yaml methods
- [#21](https://github.com/jlorieau/geomancy/issues/21). Implemented environment file loading using docker compose rules
- [#22](https://github.com/jlorieau/geomancy/issues/22). Implemented 'run' subcommand for running commands within an environment
- [#23](https://github.com/jlorieau/geomancy/issues/23). Implement ANSI color with click echo and style
- [#24](https://github.com/jlorieau/geomancy/issues/24). Implemented a simpler @env_options usage for the CLI.


### Improved Documentation

- [#6](https://github.com/jlorieau/geomancy/issues/6). Added description on file globs to running documentation
- [#21](https://github.com/jlorieau/geomancy/issues/21). Added documentation on environment file loading using docker compose rules
- [#22](https://github.com/jlorieau/geomancy/issues/22). Added documentation on the 'run' subcommand for running commands within an environment


## [0.9.1](https://github.com/jlorieau/geomancy/tree/0.9.1) - 2023-07-26


### Improved Documentation

- [#10](https://github.com/jlorieau/geomancy/issues/10). Added a more complete list of PyPI classifiers


## [0.9.0](https://github.com/jlorieau/geomancy/tree/0.9.0) - 2023-07-26


### Features

- [#17](https://github.com/jlorieau/geomancy/issues/17). Added YAML parsing functionality for checks files


### Improved Documentation

- [#17](https://github.com/jlorieau/geomancy/issues/17). Added YAML examples (default) in the documentation


## [0.8.1](https://github.com/jlorieau/geomancy/tree/0.8.1) - 2023-07-25


### Features

- [#9](https://github.com/jlorieau/geomancy/issues/9). Added the environment submodule and a CLI mechanism to load env files with -e/--env


### Improved Documentation

- [#7](https://github.com/jlorieau/geomancy/issues/7). Added base sphinx documentation
- [#8](https://github.com/jlorieau/geomancy/issues/8). Implement towncrier
