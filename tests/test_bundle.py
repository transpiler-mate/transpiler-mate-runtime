# Copyright 2026 Terradue
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from io import StringIO
from pathlib import Path
from typing import TextIO

import pytest
from cwl_loader import load_cwl_from_string_content
from cwl_utils.parser import Process
from cwl_utils.parser.cwl_v1_2 import Workflow
from ruamel.yaml import YAML
from transpiler_mate.api import (
    PluginExecutionError,
    SoftwareApplication,
    TranspilerContext,
)

from transpiler_mate.plugins.bundle import BundleOption, bundle


def _context(document: Process | tuple[Process, ...]) -> TranspilerContext:
    return TranspilerContext.model_construct(
        source=Path("workflow.cwl"),
        metadata=SoftwareApplication.model_construct(),
        document={p.id: p for p in document}
        if isinstance(document, tuple)
        else {document.id: document},
    )


def test_bundle_plugin_registration() -> None:
    assert bundle.name == "bundle"
    assert bundle.description == "Bundle the resolved CWL document to a local file."
    assert bundle.options_model is BundleOption


def test_bundle_serializes_single_process(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process = Workflow(inputs=[], outputs=[], steps=[])
    output = tmp_path / "nested" / "bundle.cwl"
    observed: dict[str, object] = {}

    def dump(process_to_dump: Process | list[Process], stream: TextIO) -> None:
        observed["document"] = process_to_dump
        stream.write("cwlVersion: v1.2\n")

    monkeypatch.setattr(
        "transpiler_mate.plugins.bundle.dump_cwl",
        dump,
    )

    bundle.execute(_context(process), BundleOption(output=output))

    assert observed["document"] == [process]
    assert output.read_text(encoding="utf-8") == "cwlVersion: v1.2\n"


def test_bundle_converts_process_index_to_dump_cwl_list(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    processes = (
        Workflow(id="first", inputs=[], outputs=[], steps=[]),
        Workflow(id="second", inputs=[], outputs=[], steps=[]),
    )
    output = tmp_path / "bundle.cwl"
    observed: dict[str, object] = {}

    def dump(process_to_dump: Process | list[Process], stream: TextIO) -> None:
        observed["document"] = process_to_dump
        stream.write("$graph: []\n")

    monkeypatch.setattr(
        "transpiler_mate.plugins.bundle.dump_cwl",
        dump,
    )

    bundle.execute(_context(processes), BundleOption(output=output))

    assert observed["document"] == list(processes)


def test_bundle_preserves_graph_and_metadata(tmp_path: Path) -> None:
    process = load_cwl_from_string_content(
        """cwlVersion: v1.2
$namespaces:
  s: https://schema.org/
s:name: Bundle regression
$graph:
- id: main
  class: Workflow
  inputs: []
  outputs: []
  steps: []
"""
    )
    output = tmp_path / "bundle.cwl"

    bundle.execute(_context(process), BundleOption(output=output))

    serialized = output.read_text(encoding="utf-8")
    document = YAML().load(StringIO(serialized))
    assert document["cwlVersion"] == "v1.2"
    assert document["$namespaces"] == {"s": "https://schema.org/"}
    assert document["s:name"] == "Bundle regression"
    assert [p["id"] for p in document["$graph"]] == ["main"]
    assert load_cwl_from_string_content(serialized).id == "main"


def test_bundle_reports_serialization_failure(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    process = Workflow(inputs=[], outputs=[], steps=[])
    output = tmp_path / "bundle.cwl"

    def dump(process_to_dump: Process | list[Process], stream: TextIO) -> None:
        del process_to_dump, stream
        raise RuntimeError("serialization failed")

    monkeypatch.setattr(
        "transpiler_mate.plugins.bundle.dump_cwl",
        dump,
    )

    with pytest.raises(
        PluginExecutionError,
        match="Unable to serialize the bundled CWL document to",
    ):
        bundle.execute(_context(process), BundleOption(output=output))
