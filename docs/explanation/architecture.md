# Architecture

`transpiler-mate-runtime` is an adapter between an API-level plugin contract
and concrete execution concerns: package discovery, command-line parsing,
source access, CWL loading, and logging.

## API and runtime separation

The `transpiler_mate` package is a native namespace shared by separately
distributed components:

- `transpiler_mate.api` defines `TranspilerPlugin`, `TranspilerContext`, option
  models, metadata models, decorators, and plugin exceptions;
- `transpiler_mate.runtime` discovers plugins, builds commands, and resolves
  contexts;
- `transpiler_mate.plugins.bundle` is the built-in plugin implementation.

This separation keeps Click out of plugin packages. A plugin can depend on the
stable API contract without coupling itself to this runtime's user interface.

## Main components

| Component | Responsibility |
| --- | --- |
| `PluginGroup` | Discover entry points and expose them as lazy Click subcommands. |
| `plugin_loader` | Read entry-point metadata, load selected objects, and validate the plugin protocol. |
| CLI field conversion | Derive Click parameters from a plugin's Pydantic option model. |
| `DefaultTranspilerContextResolver` | Configure source adapters, load CWL, validate metadata, and select a process. |
| `software_application_extractor` | Convert preserved CWL JSON-LD metadata into the API's `SoftwareApplication`. |
| `bundle` | Serialize the complete resolved CWL document to a local file. |

## Boundary of responsibility

The runtime owns how a plugin is found and invoked. A plugin owns the actual
transformation and its option schema. `cwl-loader` owns parsing and preserved
document metadata; `session-adapters` owns scheme-specific transport behavior;
the API package owns shared types.

Keeping these responsibilities explicit makes alternate front ends possible:
the plugin execution function itself accepts typed API objects and is not a
Click callback.
