# Get started

In this tutorial you will install `transpiler-mate-runtime`, inspect its
commands, and use the built-in `bundle` plugin to serialize a CWL document.

## 1. Create an environment

From a checkout of this repository, create a virtual environment and install
the package:

```console
python -m venv .venv
source .venv/bin/activate
python -m pip install .
```

On Windows PowerShell, activate the environment with
`.venv\Scripts\Activate.ps1` instead.

Confirm that the command is available:

```console
transpiler-mate --version
```

## 2. Discover the installed commands

Ask the runtime for help:

```console
transpiler-mate --help
```

The `Commands` section lists every plugin registered in the current Python
environment. This distribution registers `bundle` itself:

```text
Commands:
  bundle  Bundle the resolved CWL document to a local file.
```

Plugins are discovered lazily, so implementations are loaded only when their
command is requested.

## 3. Create a CWL document

Save the following as `hello.cwl` (the same file is available as the
[documentation example](../examples/hello.cwl)):

```yaml
cwlVersion: v1.2
class: CommandLineTool
$namespaces:
  s: https://schema.org/
s:name: Hello tool
s:description: Print a greeting
s:dateCreated: "2026-08-24"
s:license: https://spdx.org/licenses/Apache-2.0
s:softwareVersion: 1.0.0
s:softwareHelp:
  s:name: Hello tool documentation
  s:url: https://example.org/hello/help
s:publisher:
  s:name: Example organization
s:author:
  s:givenName: Ada
  s:familyName: Lovelace
  s:email: ada@example.org
  s:affiliation:
    s:name: Example organization
$graph:
  - id: hello
    class: CommandLineTool
    baseCommand: echo
    inputs:
      message:
        type: string
        default: Hello, world!
        inputBinding:
          position: 1
    outputs: []
```

The Schema.org fields are document-level metadata around `$graph`, rather than
fields on the tool inside the graph. They are not incidental: the runtime
extracts this preserved metadata and validates it as a `SoftwareApplication`
before a plugin runs.

## 4. Bundle the document

Run the built-in plugin:

```console
transpiler-mate bundle --output build/hello.bundle.cwl hello.cwl
```

The runtime creates the `build` directory if needed, loads and validates the
source, and writes the serialized document to `build/hello.bundle.cwl`. A
successful run logs `SUCCESS` and exits with status `0`.

Inspect the result:

```console
cat build/hello.bundle.cwl
```

You have now exercised the complete runtime path: plugin discovery, generated
CLI options, context resolution, metadata validation, plugin execution, and
result serialization.

## Next steps

- [Bundle CWL documents from different sources](../how-to/bundle-a-cwl-document.md)
- [Select one process in a CWL graph](../how-to/select-a-process.md)
- [Understand the execution lifecycle](../explanation/plugin-lifecycle.md)
