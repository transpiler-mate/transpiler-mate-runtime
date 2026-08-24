# Plugin lifecycle

A plugin moves through discovery, command construction, context resolution,
and execution. Each stage is delayed until it is needed.

## 1. Discovery

The root Click group queries installed metadata for the
`transpiler_mate.plugins` entry-point group. It sorts commands by name and
detects duplicate registrations without importing plugin modules.

This keeps root help responsive and prevents one unused plugin's import cost
from affecting every invocation.

## 2. Loading and command construction

When a command is requested, its entry point is loaded and checked against the
`TranspilerPlugin` protocol. The entry-point name and plugin name must agree.

The runtime then reads `plugin.options_model.model_fields` and combines the
derived plugin options with the common `SOURCE` argument and connection
options. The generated command is cached.

## 3. Option validation

Click parses individual values. The runtime omits untouched, non-required
defaults from the input dictionary so Pydantic can run default factories and
model-level logic normally. It then validates the complete options model with
both aliases and Python field names enabled.

No source is loaded when showing plugin help or when option validation fails.

## 4. Context resolution

Only immediately before execution does the command create a resolver. The
resolver mounts transport adapters, loads the CWL document, validates its
Schema.org metadata, and optionally selects a process.

The resulting `TranspilerContext` gives every plugin the same normalized view
of its input regardless of whether the source was a local path, HTTP URL, or
OCI location.

## 5. Execution and reporting

The runtime calls `plugin.execute(context, options)`. It distinguishes expected
result failures from unexpected execution errors, logs a success or failure
banner, and always reports elapsed and finish times once execution has begun.
