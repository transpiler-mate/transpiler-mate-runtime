# Bundle a CWL document

Use the built-in `bundle` plugin to load a CWL document and serialize the
resolved document to a local file.

## Bundle a local document

Pass the destination with `--output` and the source as the final argument:

```console
transpiler-mate bundle --output build/workflow.cwl workflow.cwl
```

Parent directories of the output are created automatically.

## Bundle an HTTP or HTTPS document

Use the source URL directly:

```console
transpiler-mate bundle \
  --output build/workflow.cwl \
  https://example.org/workflows/workflow.cwl
```

For a protected endpoint, add a bearer token through the environment:

```console
export OAUTH2_BEARER="your-token"
transpiler-mate bundle \
  --output build/workflow.cwl \
  https://example.org/workflows/workflow.cwl
```

You can also pass `--oauth2-bearer`, but an environment variable is less likely
to expose the token in shell history or process listings.

## Bundle an OCI document

Configure the registry connection and pass an `oci://` source:

```console
export OCI_HOSTNAME="registry.example.org"
export OCI_USERNAME="your-user"
export OCI_PASSWORD="your-password"
transpiler-mate bundle \
  --output build/workflow.cwl \
  oci://namespace/workflow:tag
```

The exact OCI path semantics are implemented by the installed
`session-adapters` package. The runtime supplies the hostname and credentials
to its OCI adapter.

## Check the result

A successful invocation logs `SUCCESS` and exits with status `0`. Expected
input or output failures log `FAILURE` or `ERROR` and exit with status `1`; CLI
usage errors exit with status `2`. See [Errors and exit codes](../reference/errors-and-exit-codes.md).

The plugin serializes the complete loaded document. Adding a `#process-id` to
the source selects a process in the context for plugins that use
`resolved_process`; it does not make the built-in `bundle` plugin extract that
process from the document.
