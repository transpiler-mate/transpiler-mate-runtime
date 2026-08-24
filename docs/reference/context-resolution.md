# Context resolution

`DefaultTranspilerContextResolver` constructs the context passed to a plugin.

## Constructor

```python
DefaultTranspilerContextResolver(
    *,
    oci_hostname: str | None = None,
    oci_username: str | None = None,
    oci_password: str | None = None,
    oauth2_bearer: str | None = None,
)
```

It creates a `requests.Session` and mounts adapters as follows:

| Scheme | Adapter |
| --- | --- |
| `http://` | `HTTPAdapter`, or `BearerAuthHTTPAdapter` when a token is supplied |
| `https://` | `HTTPAdapter`, or `BearerAuthHTTPAdapter` when a token is supplied |
| `file://` | `FileAdapter` |
| `oci://` | `OCIAdapter` configured with the supplied hostname and credentials |

## `resolve(location)`

Resolution performs these operations:

1. Split `location` at its first `#` into the load location and optional
   process ID.
2. Represent URL locations directly; represent local paths as absolute file
   URIs in `context.source`.
3. Load the CWL with `cwl_loader.load_cwl_from_location` using the configured
   session.
4. Extract and validate document-level Schema.org metadata as a
   `SoftwareApplication`.
5. If requested, locate the process ID in the loaded process or process list.
6. Return a `TranspilerContext` containing the source, metadata, document,
   selected process, and resolver.

## Returned context

| Field | Runtime value |
| --- | --- |
| `source` | A Pydantic `AnyUrl`; local paths are absolute `file:` URLs |
| `metadata` | Validated `SoftwareApplication` metadata |
| `document` | One `Process`, or a tuple when the loader returned a list |
| `resolved_process` | Selected process, the sole process, or `None` |
| `resolver` | The resolver that created the context |

For a single loaded `Process`, `resolved_process` is that process when no ID is
given. For a process list without an ID, it is `None` and a warning lists the
available IDs.

## Resolution failures

- A trailing `#` raises `PluginExecutionError`.
- Failure while loading the CWL or extracting metadata becomes
  `PluginFailureError` with the source location.
- A missing requested process becomes `PluginFailureError` listing available
  IDs.
