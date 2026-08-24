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
