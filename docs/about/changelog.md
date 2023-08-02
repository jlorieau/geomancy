# Changelog

Versions follow [semantic versioning](https://semver.org/>)
(``<major>.<minor>.<patch>``).

Changes in API will only be introduced in major versions with notes in the
deprecations section.

% Do not edit below this line, as the changelog is managed by towncrier

<!-- towncrier release notes start -->

## [1.0.0](https://github.com/jlorieau/geomancy/tree/1.0.0) - 2023-08-02


### Features

- [#11](https://github.com/jlorieau/geomancy/issues/11). Implemented --fixture option for  [✔] .geomancy.yaml...passed                                   
   [✔]   checks...passed                                         
   [✔]     Executables...passed                                  
   [✔]       Check executable 'python3 >= 3.11'...passed         
   [✔]       Check executable 'task >= 3'...passed               
   [✔]       Check executable 'sphinx-build >= 6.2'...passed     
   [✔]       Check executable 'towncrier >= 23'...passed         
   [✔]       Check executable 'twine >= 4'...passed              
   [✔]       Check executable 'pytest >= 7'...passed             
   [✔]       Check executable 'black >= 23'...passed             
   [✔]     Paths...passed                                        
   [✔]       Check path '.geomancy.yaml'...passed                
   [✔]     PythonPackages...passed                               
   [✔]       Check python package 'pyyaml >= 6.0'...passed       
   [✔]       Check python package 'click >= 8.1'...passed        
   [✔]       Check python package 'click-default-group'...passed 
   [✔]       Check python package 'rich >= 13'...passed           to mock network requests
- [#11](https://github.com/jlorieau/geomancy/issues/11). Implemented CheckAWSS3 for AWS buckets
- [#33](https://github.com/jlorieau/geomancy/issues/33). Implemented multi-threaded checking with concurrent.futures
- [#36](https://github.com/jlorieau/geomancy/issues/36). Added a project-wide .geomancy.yaml file


### Bug Fixes

- [#31](https://github.com/jlorieau/geomancy/issues/31). Fixed out-of-order rendering of check tree by implementing rich for terminal rendering


### Improved Documentation

- [#11](https://github.com/jlorieau/geomancy/issues/11). Added documentation on CheckAWSS3
- [#32](https://github.com/jlorieau/geomancy/issues/32). Implement html5 <details> and <summary> tags in the README.md features section and documentation
- [#34](https://github.com/jlorieau/geomancy/issues/34). Added API documentation


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
