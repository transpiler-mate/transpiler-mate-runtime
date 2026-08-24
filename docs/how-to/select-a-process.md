# Select a process

Append `#<process-id>` to a source location when a plugin needs one process
from a CWL graph:

```console
transpiler-mate <plugin> [PLUGIN_OPTIONS] workflow.cwl#main
```

The fragment is handled by the runtime rather than sent to the source loader.
The runtime loads `workflow.cwl`, searches the resulting process or process
list for `main`, and exposes the match as `context.resolved_process`.

The same syntax applies to remote sources:

```console
transpiler-mate <plugin> [PLUGIN_OPTIONS] \
  https://example.org/workflow.cwl#main
```

If the ID does not exist, the runtime reports the IDs that are available and
exits with status `1`. A trailing `#` with no ID is an execution error.

When a loaded document contains multiple processes and no fragment is given,
the runtime logs a warning and leaves `resolved_process` unset. The full graph
remains available through `context.document`.

!!! note
    The built-in `bundle` plugin writes `context.document`, not
    `context.resolved_process`. Process selection is therefore useful only for
    plugins that explicitly consume the selected process.
