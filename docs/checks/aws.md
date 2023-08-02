# AWS

The following describes Amazon Web Services ([AWS](https://aws.amazon.com))
checks.

## checkAwsS3

Check the existence, accessibility and, optionally, the
[security settings](https://docs.aws.amazon.com/AmazonS3/latest/userguide/security-best-practices.html) of
[AWS S3 buckets](https://aws.amazon.com/s3/).

:::{card}
Parameters
^^^
`checkAwsS3`: str
: The S3 bucket to probe using the currently configured AWS credentials. <br>
  __aliases__: ``checkS3``, ``CheckS3``, ``checkAWSS3``, ``checkAwsS3``,
  ``CheckAwsS3``

```{include} snippets/base_args.md
```

`private`: bool
: Whether to check the public availability of the bucket.<br>
  __default__: True

:::

::::{tab-set}
:::{tab-item} Example 1 (yaml)
The ``checkAwsS3`` check in YAML format.
```yaml
checks:
  AWS:
    TemplatesS3Bucket:
      desc: The bucket for cloudformation templates
      checkS3: "myproject-cfn-templates"
```
:::
:::{tab-item} Example 2 (toml)
The ``checkAwsS3`` check in TOML format.
```toml
[checks.AWS.TemplatesS3Bucket]
desc = "The bucket for cloudformation templates"
checkS3 = "myproject-cfn-templates"
```
:::
:::{tab-item} Example 3 (toml)
The ``checkAwsS3`` check in abbreviated TOML format.
```toml
[checks.AWS]
TemplatesS3Bucket = {desc = "The bucket for cloudformation templates", checkS3 = "myproject-cfn-templates"}
```
:::
::::

:::{versionadded} 1.0.0
:::
