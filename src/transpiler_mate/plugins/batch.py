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

"""Execute plugins sequentially using a YAML execution plan."""

from __future__ import annotations

from pathlib import Path
from time import perf_counter
from typing import TYPE_CHECKING, Annotated, Any

from loguru import logger
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    TypeAdapter,
    ValidationError,
)
from ruamel.yaml import YAML
from ruamel.yaml.error import YAMLError
from transpiler_mate.api import (
    PluginExecutionError,
    PluginFailureError,
    transpiler_plugin,
)

from transpiler_mate.runtime.plugin_loader import PluginLoaderError, load_plugin_by_name

if TYPE_CHECKING:
    from transpiler_mate.api import TranspilerContext


class BatchOption(BaseModel):
    """Options exposed by the runtime as CLI arguments."""

    model_config = ConfigDict(extra="forbid")

    file: Path = Field(
        default=Path("tmom.yaml"), description="YAML file describing plugin executions"
    )


_PLAN = TypeAdapter(
    dict[
        Annotated[str, StringConstraints(min_length=1, pattern=r"\S")],
        list[dict[str, Any]],
    ]
)


@transpiler_plugin(
    name="batch",
    description="Execute plugins sequentially from a YAML file using one context.",
    options_model=BatchOption,
)
def batch(context: TranspilerContext, options: BatchOption) -> None:
    """Validate the plan and invoke each plugin in document order."""
    started = perf_counter()
    logger.debug(
        f"Starting batch: file={options.file}, shared context id={id(context)}"
    )
    try:
        logger.debug(f"Opening batch execution file {options.file} as UTF-8")
        with options.file.open(encoding="utf-8") as stream:
            logger.debug("Parsing batch YAML with the safe loader")
            document = YAML(typ="safe").load(stream)
            logger.debug(
                f"Validating batch structure; root type={type(document).__name__}"
            )
            plan = _PLAN.validate_python(document, strict=True)
    except (OSError, UnicodeError) as exc:
        logger.debug(
            f"Batch file read failed: file={options.file}, error type={type(exc).__name__}"
        )
        raise PluginExecutionError(
            f"Unable to read execution file {options.file}"
        ) from exc
    except (YAMLError, ValidationError) as exc:
        logger.debug(
            f"Batch plan rejected: file={options.file}, error type={type(exc).__name__}"
        )
        raise PluginFailureError(
            f"Invalid execution file {options.file}: expected a mapping of plugin "
            f"names to arrays of input objects. {exc}"
        ) from exc

    total = sum(len(executions) for executions in plan.values())
    completed = 0
    logger.debug(f"Batch plan validated: {len(plan)} plugin groups, {total} executions")
    for group_index, (name, executions) in enumerate(plan.items(), start=1):
        logger.debug(
            f"Processing plugin group {group_index}/{len(plan)}: plugin={name!r}, executions={len(executions)}"
        )
        if not executions:
            logger.debug(f"Skipping plugin {name!r}: execution array is empty")
            continue
        try:
            logger.debug(
                f"Discovering and loading plugin {name!r} through the runtime loader"
            )
            plugin = load_plugin_by_name(name)
        except PluginLoaderError as exc:
            logger.debug(
                f"Plugin {name!r} could not be loaded: error type={type(exc).__name__}; stopping batch"
            )
            raise PluginFailureError(str(exc)) from exc
        logger.debug(
            f"Loaded plugin {name!r}: options model={plugin.options_model.__name__}"
        )
        # A batch cannot invoke itself: its default file would recurse forever.
        if plugin.execute is batch.execute:
            logger.debug(
                f"Rejecting recursive batch invocation through plugin {name!r}"
            )
            raise PluginFailureError("A batch plan cannot invoke the batch plugin")
        for index, inputs in enumerate(executions, start=1):
            logger.info(
                "------------------------------------------------------------------------"
            )
            logger.debug(
                f"Validating plugin {name!r} execution {index}/{len(executions)}: {len(inputs)} supplied fields"
            )
            try:
                plugin_options = plugin.options_model.model_validate(
                    inputs, by_alias=True, by_name=True
                )
            except ValidationError as exc:
                logger.debug(
                    f"Options rejected for plugin {name!r}, execution {index}: {exc.error_count()} validation errors; stopping batch"
                )
                raise PluginFailureError(
                    f"Invalid options for plugin {name!r}, execution {index}: {exc}"
                ) from exc
            logger.debug(f"Options validated for plugin {name!r}, execution {index}")
            execution_started = perf_counter()
            logger.info(
                f"Starting plugin {name!r} execution {index}/{len(executions)} (batch execution {completed + 1}/{total}), shared context id={id(context)}"
            )
            try:
                plugin.execute(context, plugin_options)
            except Exception as exc:
                logger.debug(
                    f"Plugin {name!r} execution {index} failed after {perf_counter() - execution_started:.4f}s: error type={type(exc).__name__}; stopping batch with {completed}/{total} executions completed"
                )
                raise
            completed += 1
            logger.success(
                f"Completed plugin {name!r} execution {index} in {perf_counter() - execution_started:.4f}s; batch progress={completed}/{total}"
            )
        logger.debug(f"Completed plugin group {name!r}: {len(executions)} executions")
    logger.debug(
        f"Batch completed: file={options.file}, executions={completed}/{total}, elapsed={perf_counter() - started:.4f}s"
    )


__all__ = ["BatchOption", "batch"]
