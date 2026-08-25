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

from pathlib import Path
from typing import TYPE_CHECKING

from cwl_loader import _is_url, load_cwl_from_location
from cwl_loader.utils import to_index
from loguru import logger
from pydantic import AnyUrl
from requests import Session
from requests.adapters import BaseAdapter, HTTPAdapter
from session_adapters.bearer_auth_http_adapter import BearerAuthHTTPAdapter
from session_adapters.file_adapter import FileAdapter
from session_adapters.oci_adapter import OCIAdapter
from transpiler_mate.api import (
    PluginExecutionError,
    PluginFailureError,
    TranspilerContextResolver,
)
from transpiler_mate.api.plugin import TranspilerContext

from .software_application_extractor import software_application_from_process

if TYPE_CHECKING:
    from cwl_utils.parser import Process
    from transpiler_mate.api import SoftwareApplication


class DefaultTranspilerContextResolver(TranspilerContextResolver):
    def __init__(
        self,
        *,
        oci_hostname: str | None = None,
        oci_username: str | None = None,
        oci_password: str | None = None,
        oauth2_bearer: str | None = None,
    ) -> None:
        self._session = Session()

        http_adapter = (
            BearerAuthHTTPAdapter(oauth2_bearer) if oauth2_bearer else HTTPAdapter()
        )
        self._mount_session("http://", http_adapter)
        self._mount_session("https://", http_adapter)
        self._mount_session("file://", FileAdapter())
        self._mount_session(
            "oci://",
            OCIAdapter(
                hostname=oci_hostname,
                username=oci_username,
                password=oci_password,
            ),
        )

    def _mount_session(self, scheme: str, adapter: BaseAdapter) -> None:
        logger.debug(f"Mounting '{scheme}' scheme to '{type(adapter).__name__}'...")
        self._session.mount(scheme, adapter)
        logger.debug(
            f"Scheme '{scheme}' successfully mount to '{type(adapter).__name__}'"
        )

    def resolve(self, location: str) -> TranspilerContext:
        location_source, separator, process_id = location.partition("#")

        if separator and not process_id:
            raise PluginExecutionError(f"Empty #<process-id> in location '{location}'")

        source: AnyUrl = (
            AnyUrl(location_source)
            if _is_url(path_or_url=location_source, session=self._session)
            else AnyUrl(Path(location_source).absolute().as_uri())
        )

        try:
            cwl_document: list[Process] | Process = load_cwl_from_location(
                path=location_source, session=self._session
            )

            metadata: SoftwareApplication = software_application_from_process(
                cwl_document
            )

            return TranspilerContext(
                source=source,
                metadata=metadata,
                document=to_index(
                    cwl_document if isinstance(cwl_document, list) else [cwl_document]
                ),
                process_id=process_id,
                resolver=self,
            )
        except Exception as exc:
            raise PluginFailureError(
                f"Impossible to load a CWL document from {location_source}"
            ) from exc
