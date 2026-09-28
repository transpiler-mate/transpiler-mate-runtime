# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.3.0] - 2026-09-28

### Changed

- dynamic resolution of the `authfile` according to the requirements below:
    - on Linux, the default is `${XDG_RUNTIME_DIR}/containers/auth.json`;
    - the default value of this option is read from the `REGISTRY_AUTH_FILE` environment variable.

Refs: https://github.com/podman-container-tools/skopeo/blob/main/docs/skopeo-login.1.md
Refs: https://man.archlinux.org/man/containers-auth.json.5

## [1.2.0] - 2026-09-28

### Added

- Support for registry credentials files in the [containers-auth.json format](https://man.archlinux.org/man/containers-auth.json.5) through the `--authfile` option and the context resolver's `authfile` argument.

### Changed

- Require `session-adapters>=0.6.0` for OCI authentication using the shared credentials model.

### Fixed

- Update OCI adapter test mocks for the credentials model and resolve type-checking, import-order, and formatting errors.

## [1.1.1] - 2026-09-27

### Added

- Each plugin execution prints the installed plugin version. 

### Changed

- Improve type annotations and internal code quality by addressing mypy, Ruff, and Bandit findings, without changing public APIs or runtime behavior.

## [1.1.0] - 2026-09-18

### Added

- Initial implementation of the built-in `batch` plugin.

## [1.0.1] - 2026-09-09

### Fixed

- `bundle` plugin invoked the documents index rather than the `Process` list.

## [1.0.0] - 2026-09-04

### Added

- Initial release.

[unreleased]: https://github.com/Transpiler-Mate/transpiler-mate-runtime/compare/v1.3.0...HEAD
[1.3.0]: https://github.com/Transpiler-Mate/transpiler-mate-runtime/compare/v1.2.0...v1.3.0
[1.2.0]: https://github.com/Transpiler-Mate/transpiler-mate-runtime/compare/v1.1.1...v1.2.0
[1.1.1]: https://github.com/Transpiler-Mate/transpiler-mate-runtime/compare/v1.0.1...v1.1.1
[1.1.0]: https://github.com/Transpiler-Mate/transpiler-mate-runtime/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/Transpiler-Mate/transpiler-mate-runtime/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/Transpiler-Mate/transpiler-mate-runtime/releases/tag/v1.0.0
