# Register a plugin

A plugin distribution becomes a `transpiler-mate` subcommand by registering a
`TranspilerPlugin` object in the `transpiler_mate.plugins` entry-point group.

## 1. Define its options and execution function

Use the API package's decorator and a Pydantic model:

```python
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field
from transpiler_mate.api import TranspilerContext, transpiler_plugin


class ExampleOptions(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output: Path = Field(description="Destination file")
    verbose: bool = Field(default=False, description="Enable verbose output")


@transpiler_plugin(
    name="example",
    description="Run the example transpiler.",
    options_model=ExampleOptions,
)
def plugin(context: TranspilerContext, options: ExampleOptions) -> None:
    source = context.source
    process = context.resolved_process
    # Perform the transformation and write options.output.
```

The runtime converts model fields into Click options. Required fields become
required options, field descriptions become help text, and optional Boolean
fields become `--name/--no-name` flag pairs.

## 2. Register the entry point

If the module above is `example_plugin/__init__.py`, add this to the plugin
package's `pyproject.toml`:

```toml
[project.entry-points."transpiler_mate.plugins"]
example = "example_plugin:plugin"
```

The entry-point name must equal the plugin's `name`. The runtime rejects a
mismatch when the command is requested.

## 3. Install and verify the plugin

Install the plugin distribution into the same environment as the runtime:

```console
python -m pip install -e /path/to/example-plugin
transpiler-mate --help
transpiler-mate example --help
```

The root help should list `example`, while the plugin help should show
`SOURCE`, the shared connection options, `--output`, and the Boolean flag pair.

## 4. Report failures deliberately

Raise the API's `PluginFailureError` for an expected inability to produce a
result. Raise `PluginExecutionError` for an unexpected technical failure. Both
produce status `1`, but the runtime logs a traceback only for the latter.

Other `PluginError` subclasses are presented as Click errors. See
[Errors and exit codes](../reference/errors-and-exit-codes.md).
