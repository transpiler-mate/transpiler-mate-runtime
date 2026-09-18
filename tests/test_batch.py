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

# This workflow will install Python dependencies, run tests and lint with a single version of Python
# For more information see: https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python

from pathlib import Path
from unittest.mock import Mock

import pytest
from click.testing import CliRunner
from pydantic import BaseModel, Field
from transpiler_mate.api import (
    PluginExecutionError,
    PluginFailureError,
    TranspilerContext,
    TranspilerPlugin,
    transpiler_plugin,
)

from transpiler_mate.plugins.batch import BatchOption, batch
from transpiler_mate.runtime.cli import plugin_to_click_command
from transpiler_mate.runtime.plugin_loader import PluginNotFoundError


class Options(BaseModel):
    count: int = Field(alias="number")


def test_order_models_and_shared_context(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = tmp_path / "tmom.yaml"
    plan.write_text('second:\n  - number: "2"\n  - count: 3\nfirst:\n  - number: 4\n')
    context = TranspilerContext.model_construct()
    calls = []

    def plugin(name: str) -> TranspilerPlugin[Options]:
        @transpiler_plugin(name=name, description=name, options_model=Options)
        def execute(ctx: TranspilerContext, options: Options) -> None:
            assert ctx is context
            assert isinstance(options, Options)
            calls.append((name, options.count))

        return execute

    plugins = {name: plugin(name) for name in ("first", "second")}
    monkeypatch.setattr(
        "transpiler_mate.plugins.batch.load_plugin_by_name", plugins.__getitem__
    )
    monkeypatch.chdir(tmp_path)
    batch.execute(context, BatchOption())
    assert calls == [("second", 2), ("second", 3), ("first", 4)]


@pytest.mark.parametrize(
    "content",
    [
        "",
        "[]",
        "foo: {}",
        "foo: [null]",
        "foo: [3]",
        "1: []",
        "'': []",
        "foo: [{}]\nbar: null",
        "foo: []\nfoo: []",
        "foo: [",
    ],
)
def test_invalid_plan_before_loading(
    content: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = tmp_path / "plan.yaml"
    plan.write_text(content)
    loader = Mock()
    monkeypatch.setattr("transpiler_mate.plugins.batch.load_plugin_by_name", loader)
    with pytest.raises(PluginFailureError, match="Invalid execution file"):
        batch.execute(TranspilerContext.model_construct(), BatchOption(file=plan))
    loader.assert_not_called()


def test_missing_file(tmp_path: Path) -> None:
    with pytest.raises(PluginExecutionError, match="Unable to read"):
        batch.execute(
            TranspilerContext.model_construct(), BatchOption(file=tmp_path / "missing")
        )


@pytest.mark.parametrize(
    "failure", [PluginFailureError("failed"), PluginExecutionError("broken")]
)
def test_stops_on_failure(
    failure: Exception, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = tmp_path / "plan.yaml"
    plan.write_text("foo: [{count: 1}, {count: 2}]\nbar: [{count: 3}]")
    execute = Mock(side_effect=failure)
    loader = Mock(return_value=Mock(options_model=Options, execute=execute))
    monkeypatch.setattr("transpiler_mate.plugins.batch.load_plugin_by_name", loader)
    with pytest.raises(type(failure), match=str(failure)):
        batch.execute(TranspilerContext.model_construct(), BatchOption(file=plan))
    assert execute.call_count == 1
    loader.assert_called_once_with("foo")


def test_cli_file_option() -> None:
    result = CliRunner().invoke(plugin_to_click_command(batch), ["--help"])
    assert result.exit_code == 0
    assert "--file" in result.output
    assert "tmom.yaml" in result.output


@pytest.mark.parametrize("kind", ["unknown", "options", "recursive"])
def test_invalid_execution(
    kind: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    plan = tmp_path / "plan.yaml"
    plan.write_text("foo: [{}]")
    loader = Mock(return_value=Mock(options_model=Options))
    if kind == "unknown":
        loader.side_effect = PluginNotFoundError("foo", "transpiler_mate.plugins")
    elif kind == "recursive":
        loader.return_value = batch
    monkeypatch.setattr("transpiler_mate.plugins.batch.load_plugin_by_name", loader)
    with pytest.raises(PluginFailureError):
        batch.execute(TranspilerContext.model_construct(), BatchOption(file=plan))
