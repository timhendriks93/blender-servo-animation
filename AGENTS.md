# AGENTS.md

## Project Overview

This repository contains a Blender add-on that converts armature animation into servo position data and can stream live servo commands over serial or websocket connections.

The extension source lives in `addon/`. Example assets are in `examples/`. Blender-driven integration tests live in `tests/integration/`.

## Key Paths

- `addon/__init__.py`: add-on registration entry point
- `addon/ops/`: export and live mode operators
- `addon/props/`: Blender property groups
- `addon/ui/`: Blender panels and menus
- `addon/utils/`: conversion logic, live mode helpers, and servo settings helpers
- `tests/test.py`: unittest discovery entry point used inside Blender
- `tests/prepare.py`: installs Python dependencies into Blender's Python environment
- `scripts/build.sh`: builds the Blender extension zip
- `scripts/install.sh`: installs the built extension into Blender
- `scripts/prepare.sh`: runs dependency preparation in Blender
- `scripts/test.sh`: runs the integration suite in Blender

## Working Conventions

- Preserve Blender add-on compatibility patterns already used in the repo. Registration is centralized in `addon/__init__.py`.
- Favor small, local changes. Operator, UI, property, and utility responsibilities are already split by folder.
- Do not assume plain Python execution is enough for behavior verification. Most meaningful tests run through Blender with the test `.blend` file.
- `requirements-dev.txt` is also intended for local development inside the repo `venv`. Installing it there supports IDE hints, local imports, and linting.
- Keep dependencies aligned with `requirements-dev.txt` and the vendored wheels in `addon/wheels/` when relevant to live mode functionality.

## Validation

Typical project workflows:

- Install local development dependencies into the repo `venv`: `./.venv/bin/pip install -r requirements-dev.txt`
- Lint add-on code: `./.venv/bin/pylint addon`
- Lint tests: `./.venv/bin/pylint -d duplicate-code tests`
- Prepare Blender's Python environment: `scripts/prepare.sh`
- Run integration tests: `scripts/test.sh`
- Build extension package: `scripts/build.sh`
- Install built package into Blender: `scripts/install.sh`

## Editing Guidance

- Avoid reverting unrelated work in the tree.
- If modifying live mode behavior, review both serial and websocket paths plus any jump-handling or calibration flows.
- If changing export behavior, check JSON, binary, and text/header outputs together because they share conversion logic.
- When updating user-facing behavior, keep `README.md` in sync if the workflow, UI, or feature set changes.
