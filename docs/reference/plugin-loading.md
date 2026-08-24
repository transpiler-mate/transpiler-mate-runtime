# Plugin loading

## Entry-point group

The default group is:

```text
transpiler_mate.plugins
```

An entry-point name is the discovery identifier and must match the loaded
plugin's `name` when exposed through the CLI.

## Public loader API

All names below are exported by `transpiler_mate.runtime.plugin_loader`.

### `discover_plugins(group=PLUGIN_ENTRY_POINT_GROUP)`

Reads installed entry-point metadata without importing implementations.
Returns a dictionary ordered lexicographically by entry-point name.

Raises `DuplicatePluginError` when multiple distributions register the same
name. If several names are duplicated, the lexicographically first duplicate
is reported.

### `find_plugin(name, group=PLUGIN_ENTRY_POINT_GROUP)`

Discovers plugins and returns the matching `importlib.metadata.EntryPoint`
without loading it. Raises `PluginNotFoundError` if it is absent.

### `load_plugin(entry_point)`

Calls `entry_point.load()` and verifies that the result satisfies the runtime
`TranspilerPlugin` protocol. Raises:

- `PluginLoadError` when importing or resolving the entry point fails;
- `InvalidPluginError` when the loaded object does not implement the protocol.

### `load_plugin_by_name(name, group=PLUGIN_ENTRY_POINT_GROUP)`

Combines `find_plugin` and `load_plugin`.

### `load_plugins(group=PLUGIN_ENTRY_POINT_GROUP)`

Discovers and loads all plugins, returning a name-to-plugin dictionary.

## CLI caching

The root command caches discovered entry-point metadata for the lifetime of its
Click group instance. It also caches each generated command after loading that
plugin. Listing commands does not import plugin implementations.
