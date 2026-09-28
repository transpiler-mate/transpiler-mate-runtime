# Access remote sources

Every plugin command accepts the same runtime connection options. Place them
after the plugin name and before or after other plugin options:

```console
transpiler-mate <plugin> [RUNTIME_OPTIONS] [PLUGIN_OPTIONS] SOURCE
```

## Authenticate to HTTP and HTTPS

Set a bearer token:

```console
export OAUTH2_BEARER="your-token"
transpiler-mate <plugin> [PLUGIN_OPTIONS] https://example.org/tool.cwl
```

Or pass it directly:

```console
transpiler-mate <plugin> \
  --oauth2-bearer "your-token" \
  [PLUGIN_OPTIONS] \
  https://example.org/tool.cwl
```

Without a token, the runtime uses a standard HTTP adapter. With a token, it
mounts a bearer-authentication adapter for both HTTP and HTTPS.

## Authenticate to OCI

!!! warning "Available from version 1.2.0"

    Support for registry credentials files in the
    [containers-auth.json format](https://man.archlinux.org/man/containers-auth.json.5)
    is available from **transpiler-mate-runtime 1.2.0**. Earlier versions do not
    support the `--authfile` option.

Pass the credentials file explicitly:

```console
transpiler-mate <plugin> \
  --authfile /path/to/containers/auth.json \
  [PLUGIN_OPTIONS] \
  oci://namespace/tool:tag
```

The file must contain a JSON object. An empty object (`{}`) supplies no registry
credentials. Without `--authfile`, the runtime starts with an empty credential
set; it does not automatically discover a credentials file.

You can also supply credentials through environment variables:

```console
export OCI_HOSTNAME="registry.example.org"
export OCI_USERNAME="your-user"
export OCI_PASSWORD="your-password"
transpiler-mate <plugin> [PLUGIN_OPTIONS] oci://namespace/tool:tag
```

The equivalent command options are `--oci-hostname`, `--oci-username`, and
`--oci-password`.

## Select a process in a remote document

Append a fragment to the source:

```console
transpiler-mate <plugin> [PLUGIN_OPTIONS] \
  oci://namespace/workflow:tag#main
```

See [Select a process](select-a-process.md) for the selection behavior.

!!! warning
    Command-line secrets may be recorded in shell history and visible to other
    local processes. Prefer the supported environment variables or your
    platform's secret injection facility.
