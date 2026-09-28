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

"""Resolve CWL documents and configure authenticated transport adapters."""

import json
from pathlib import Path
from typing import TYPE_CHECKING

from cwl_loader import _is_url, load_cwl_from_location
from cwl_loader.utils import to_index
from loguru import logger
from pydantic import AnyUrl
from requests import Session
from requests.adapters import BaseAdapter, HTTPAdapter
from session_adapters.bearer_auth_http_adapter import BearerAuthHTTPAdapter
from session_adapters.conainers_auth import ContainersAuth
from session_adapters.file_adapter import FileAdapter
from session_adapters.oci_adapter import OCIAdapter, add_auth
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


def read_authfile(path: Path) -> ContainersAuth:
    """Load registry credentials from a JSON file.

    An empty object produces an empty credential set.

    Raises:
        PluginExecutionError: If the JSON document is not an object.
        OSError: If the file cannot be read.
        ValueError: If the JSON or credential structure is invalid.
    """
    with path.open(encoding="utf-8") as stream:
        document = json.load(stream)

    if not isinstance(document, dict):
        raise PluginExecutionError(f"Auth file {path.absolute()} must contain a JSON object")

    # An empty config_dict otherwise triggers automatic file discovery.
    if not document:
        return ContainersAuth(auths={})

    return ContainersAuth.model_validate(document, by_alias=True)


class DefaultTranspilerContextResolver(TranspilerContextResolver):
    def __init__(
        self,
        *,
        oci_hostname: str | None = None,
        oci_username: str | None = None,
        oci_password: str | None = None,
        authfile: str | None = None,
        oauth2_bearer: str | None = None,
    ) -> None:
        self._session = Session()

        http_adapter = BearerAuthHTTPAdapter(oauth2_bearer) if oauth2_bearer else HTTPAdapter()
        self._mount_session("http://", http_adapter)
        self._mount_session("https://", http_adapter)
        self._mount_session("file://", FileAdapter())

        # OCI containers auth
        containers_auth: ContainersAuth = (
            read_authfile(Path(authfile)) if authfile else ContainersAuth(auths={})
        )
        if oci_hostname and oci_username and oci_password:
            add_auth(oci_hostname, oci_username, oci_password, containers_auth)
        self._mount_session("oci://", OCIAdapter(containers_auth))

    def _mount_session(self, scheme: str, adapter: BaseAdapter) -> None:
        logger.debug(f"Mounting '{scheme}' scheme to '{type(adapter).__name__}'...")
        self._session.mount(scheme, adapter)
        logger.debug(f"Scheme '{scheme}' successfully mount to '{type(adapter).__name__}'")

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

            metadata: SoftwareApplication = software_application_from_process(cwl_document)

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
