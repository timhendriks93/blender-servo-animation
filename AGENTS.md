# AGENTS

## Test Workflow

Run all commands from the repository root.

Before running the Blender integration tests, install the test dependencies into Blender's Python environment:

```bash
bash scripts/prepare.sh
```

Then run the test suite:

```bash
bash scripts/test.sh
```

The prepare step is required because the integration tests depend on packages such as `parameterized`, and those must be installed inside Blender's Python environment.

## Verification Expectations

Agents should always verify code changes by running the relevant tests before finishing work.

- If a change affects live mode, export behavior, calibration, or other tested Blender flows, run `bash scripts/test.sh`.
- If the test dependencies may not be installed yet in the current environment, run `bash scripts/prepare.sh` first.
- If tests cannot be run, explicitly say so and explain why.

## Test Coverage Expectations

Behavior changes should be covered by tests.

- Prefer extending existing integration tests when the changed behavior already has coverage nearby.
- Write new tests when no existing test covers the behavior being introduced or changed.
- When behavior intentionally changes, update the affected tests so they describe the new behavior rather than preserving outdated expectations.
