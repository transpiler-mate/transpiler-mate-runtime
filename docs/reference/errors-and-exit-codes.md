# Errors and exit codes

## Exit statuses

| Status | Meaning |
| --- | --- |
| `0` | Plugin completed successfully, or an informational option such as `--help` or `--version` completed. |
| `1` | Context creation or plugin execution failed. |
| `2` | Click rejected command syntax or the plugin options failed Pydantic validation. |

## Plugin errors

| Exception | CLI presentation |
| --- | --- |
| `PluginFailureError` | Logs `FAILURE` and the expected failure without a traceback; exits `1`. |
| `PluginExecutionError` | Logs `ERROR` and a traceback for an unexpected technical failure; exits `1`. |
| Other `PluginError` | Converted to a `click.ClickException`. |

After plugin invocation begins, the runtime logs start time, finish time, and
elapsed seconds whether execution succeeds or fails.

## Loader errors

All loader exceptions derive from `PluginLoaderError`:

| Exception | Condition |
| --- | --- |
| `DuplicatePluginError` | More than one installed entry point has the same name. |
| `PluginNotFoundError` | No entry point has the requested name. |
| `PluginLoadError` | `EntryPoint.load()` raised an exception. |
| `InvalidPluginError` | The loaded object does not implement `TranspilerPlugin`. |

Discovery and loading errors encountered by the Click group are presented as
Click errors.

## Option validation

The generated command first converts individual values, then validates the
complete plugin options model with aliases and field names enabled. Complete
model failures are rendered as:

```text
Invalid plugin options:
  field.path: validation message
```
