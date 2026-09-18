# Batch plugin

Available since version **1.1.0**, the `batch` plugin runs multiple plugin
executions sequentially with the same resolved CWL context. An execution plan
in YAML specifies the plugins and their inputs.

## Command

```text
transpiler-mate batch [OPTIONS] SOURCE
```

`SOURCE` is the CWL document, as with other plugin commands. In addition to the
[shared runtime options](cli.md), the plugin accepts:

| Option | Required | Default | Description |
| --- | --- | --- | --- |
| `--file PATH` | no | `tmom.yaml` | UTF-8 YAML file describing plugin executions |

The plugin's `BatchOption` model defines this option; the runtime generates the
CLI option from the model.

## Execution file

`tmom` stands for **Transpiler Mate Object Model**.

Create `tmom.yaml` in your working directory:

```yaml
bundle:
  - output: build/workflow.cwl
  - output: build/copy.cwl
```

Then run:

```console
transpiler-mate batch workflow.cwl
```

To use a different execution file:

```console
transpiler-mate batch workflow.cwl --file plans/release.yaml
```

The file must contain a mapping with this structure:

- Each key is a nonblank string naming an installed plugin's entry point.
- Each value is an array of executions for that plugin.
- Each execution is an object whose string keys and values supply the target
  plugin's options model. Use `{}` when an execution needs only model defaults.

For multiple plugins, add another key with its own execution array. For example,
if you have installed a plugin named `report` with an `output` option:

```yaml
bundle:
  - output: build/workflow.cwl
  - output: build/copy.cwl
report:
  - output: build/report.json
```

Both `bundle` executions finish before `report` starts. `report` is an illustrative
external plugin, not included with this runtime.

Relative execution-file paths resolve from the working directory. Input values
are passed to each target model; the batch plugin does not rebase paths relative
to the YAML file.

## Validation and execution

The plugin parses YAML using the existing Ruamel.YAML safe loader and validates
the complete file structure before loading or executing any target plugin.
Empty documents, duplicate keys, non-mapping roots, non-array execution groups,
and non-object execution items are rejected. An empty mapping (`{}`) is a valid
no-op; empty execution arrays are skipped without loading their plugin.

Plugins run in the order their keys appear in the file, and each plugin's
executions run in array order. The runtime's existing plugin loader discovers
and loads each target. Immediately before each execution, the target's options
model validates its inputs, applies defaults, and performs its normal type
conversion. Both field names and aliases are accepted.

Every execution receives the same context instance. The CWL source is resolved
once by the runtime, and batch does not create a new context for each execution.
Nested batch invocations are rejected.

## Failures and debug logging

Execution stops at the first failure. Earlier executions are not rolled back;
option validation for a later execution can fail after earlier executions have
already completed.

Unreadable files raise `PluginExecutionError`. Invalid YAML, invalid plan
structure, plugin loading failures, invalid target options, and recursive batch
invocations raise `PluginFailureError`. Exceptions raised by target plugins
propagate unchanged to the runtime's [error handling](errors-and-exit-codes.md).

Debug messages cover file parsing, structure validation, plugin loading, options
validation, shared context identity, execution progress, timings, skipped groups,
and failures. These debug messages omit input values.
