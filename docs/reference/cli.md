# Command-line interface

## Root command

```text
transpiler-mate [OPTIONS] COMMAND [ARGS]...
```

| Option | Behavior |
| --- | --- |
| `--version` | Print the installed `transpiler-mate-runtime` version and exit. |
| `--help` | List global options and discovered plugin commands. |

Connection options do not appear on the root command. They belong to every
dynamically generated plugin command.

## Plugin commands

```text
transpiler-mate PLUGIN [OPTIONS] SOURCE
```

`SOURCE` is required. It can be a local path or a location handled by a mounted
HTTP, HTTPS, file, or OCI session adapter. A `#process-id` suffix requests one
process from the loaded document.

Every plugin command receives these runtime options:

| Option | Environment variable | Value |
| --- | --- | --- |
| `--oci-hostname` | `OCI_HOSTNAME` | OCI registry hostname |
| `--oci-username` | `OCI_USERNAME` | OCI username |
| `--oci-password` | `OCI_PASSWORD` | OCI password |
| `--oauth2-bearer` | `OAUTH2_BEARER` | Bearer token for HTTP and HTTPS |

Plugin-specific options follow the plugin's Pydantic `options_model`.

## Pydantic-to-Click mapping

| Pydantic annotation or field | Click representation |
| --- | --- |
| `str` | text option |
| `int` | integer option |
| `float` | floating-point option |
| `Path` | path option returning `pathlib.Path` |
| Required `bool` | Boolean-valued option |
| Optional/defaulted `bool` | `--field/--no-field` flag pair |
| `Enum` | case-insensitive choice using member names |
| `Literal[...]` | case-sensitive choice preserving the original value type |
| `list[T]`, `set[T]`, `frozenset[T]`, `Sequence[T]` | repeatable option |
| `tuple[T, ...]` | repeatable option |
| Fixed `tuple[T1, T2, ...]` | fixed-width tuple option |
| `T | None` or `Optional[T]` | mapped as `T`; requiredness still comes from the field |
| Other annotations | value parsed by a Pydantic `TypeAdapter` |

Field names replace underscores with hyphens. For example, `output_path`
becomes `--output-path`. Descriptions supply option help, and static defaults
are displayed when non-null. Values are validated again by the complete
Pydantic model before context resolution begins, so cross-field and constrained
field validation still applies.

Collection options may be repeated:

```console
transpiler-mate example --tags alpha --tags beta source.cwl
```

An enum member such as `Mode.FAST` is shown as `fast` and converted back to the
enum value before model validation.
