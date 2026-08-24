# CWL metadata

The runtime treats document metadata as part of the plugin input contract, not
as unstructured decoration. Before any plugin executes, the metadata must
validate as the `SoftwareApplication` model supplied by
`transpiler-mate-api`.

## Why preserved metadata is used

For graph documents, `cwl-loader` parses `$graph` into
`cwl_utils.parser.Process` objects while preserving the surrounding
document-level metadata. The extractor reads that preserved mapping instead of
serializing the parsed process back to YAML or JSON.

This matters because parser objects represent the executable CWL structure,
while the preserved mapping retains JSON-LD terms and the document's namespace
context.

In the currently supported loader behavior, this preserved mapping comes from
fields surrounding `$graph`. A standalone process without a `$graph` wrapper
does not provide the document-level metadata expected by the extractor.

## Conversion process

The extractor performs four operations:

1. obtain the first available preserved document-level metadata mapping;
2. make a deep copy so JSON-LD processing cannot mutate the parser's retained
   metadata;
3. use `$namespaces` as the expansion context and compact into an empty output
   context, producing canonical IRIs;
4. validate the compacted mapping as `SoftwareApplication` with aliases
   enabled.

The empty output context is intentional: model aliases can match canonical
Schema.org IRIs without relying on whichever short prefix the source document
chose.

## Failure boundary

The extractor itself distinguishes missing preserved metadata from JSON-LD and
Pydantic validation errors. During context resolution, all loading and metadata
extraction failures are wrapped as `PluginFailureError` saying that the source
could not be loaded as a CWL document.

Consequently, plugin code can assume that `context.metadata` is already a
validated `SoftwareApplication`.
