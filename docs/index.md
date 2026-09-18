# transpiler-mate-runtime

`transpiler-mate-runtime` discovers and runs plugins that transform Common
Workflow Language (CWL) documents. It provides the `transpiler-mate` command,
turns plugin option models into command-line options, resolves local and remote
CWL sources, and supplies a built-in `bundle` plugin.

!!! tip "New in version 1.1.0: batch plugin"

    Run multiple plugins sequentially with the same CWL context using the
    [batch plugin](reference/batch-plugin.md). Define executions in `tmom.yaml`,
    or select another file with `--file`.

This package is the runtime layer. Plugin contracts and shared data models live
in the separately distributed `transpiler-mate-api` package, so plugin packages
can depend on the API without depending on the Click-based runtime.

## Choose what you need

- Follow [Get started](tutorials/getting-started.md) to install the runtime and
  bundle your first CWL document.
- Use the [how-to guides](how-to/index.md) when you have a specific task, such
  as accessing an OCI source or registering a plugin.
- Consult the [reference](reference/index.md) for exact CLI, loader, resolver,
  and error behavior.
- Read the [explanation](explanation/index.md) to understand the architecture,
  lifecycle, and metadata design.

## Requirements

- Python 3.10 or later
- A CWL document carrying the Schema.org `SoftwareApplication` metadata
  required by `transpiler-mate-api`
- Any plugin-specific dependencies and credentials

The project is licensed under the Apache License 2.0.
