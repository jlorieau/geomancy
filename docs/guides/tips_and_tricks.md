# Tips and Tricks

## Unwanted environment substitution

Environment variables are substituted by default in the values passed to
checks. This can be avoided by setting ``substitute`` to False or by
using a literal with single quotes.

::::{tab-set}
:::{tab-item} Substitute (yaml)
```yaml
MyOddFilename:
  checkPath: myfile$.txt
  substitution: False
```
:::
:::{tab-item} Literal string (yaml)
Use triple (3) single quotes
```yaml
MyOddFilename:
  checkPath: '''myfile$.txt'''
```
:::
:::{tab-item} Substitute (toml)
```yaml
[MyOddFilename]
checkpath='myfile$.txt'
substitution=false
```
:::
:::{tab-item} Literal string (toml)
Use quadruple (4) single quotes
```yaml
[MyOddFilename]
checkpath=''''myfile$.txt''''
```
:::
::::

## Flat Checks files

Checks can be conveniently grouped by category, but this is not a strict
requirement for checks files. For example, the following checks file
includes checks at the root level.

::::{tab-set}
:::{tab-item} Example 1 (yaml)
```yaml
Geomancy:
  desc: Check for the 'geomancy.toml' file
  checkPath: examples/geomancy.toml
  type: file

Pyproject:
  desc: Check for 'pyproject.toml' file
  checkPath: examples/pyproject.toml
  type: file
```
:::
:::{tab-item} Example 2 (toml)
```toml
[Geomancy]
desc = "Check for the 'geomancy.toml' file"
checkPath = "examples/geomancy.toml"
type = "file"

[Pyproject]
desc = "Check for 'pyproject.toml' file"
checkPath = "examples/pyproject.toml"
type = "file"
```
:::
::::
