# Built-in bundle plugin

The runtime distribution registers this entry point:

```toml
[project.entry-points."transpiler_mate.plugins"]
bundle = "transpiler_mate.plugins.bundle:bundle"
```

## Command

```text
transpiler-mate bundle [OPTIONS] SOURCE
```

In addition to the shared runtime options, it accepts:

| Option | Required | Description |
| --- | --- | --- |
| `--output PATH` | yes | Local path where the bundled CWL document is written |

## Behavior

The plugin:

1. reads the complete `context.document`;
2. converts a tuple of processes back to a list for `cwl_loader.dump_cwl`;
3. creates the output's parent directories;
4. opens the output as UTF-8 text;
5. serializes the CWL document with `dump_cwl`.

It does not serialize `context.resolved_process`. A source fragment can select
a process for other plugins, but does not change which document the bundle
plugin writes.

Any directory creation, file opening, or serialization exception is wrapped in
`PluginExecutionError`.
