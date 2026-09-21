# Publishing a Windows release

Publish the standalone executable as an asset in
[GitHub Releases](https://github.com/KValevska/AGtest-framework/releases).
The repository contains the source and build configuration; `dist/` is a local
build output and is intentionally ignored by Git.

GitHub blocks regular repository files larger than 100 MiB. Releases are the
supported place to distribute large binaries; see
[GitHub's large-file documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

## Prepare the files

1. Review and commit the source, documentation, and build configuration for the
   release. Push that commit to GitHub.
2. On Windows x64 with Python 3.11, build from that same commit:

   ```powershell
   powershell -NoProfile -ExecutionPolicy Bypass -File .\build_exe.ps1
   ```

3. Confirm that the build and standalone self-test pass. The report is in
   `build/standalone-self-test.json`; dependency versions are recorded in
   `build/build-environment.txt`.
4. The two files to upload are:

   | File | Purpose |
   | --- | --- |
   | `dist/AGtest-framework.exe` | Single-file Windows application, with Python and dependencies included |
   | `dist/SHA256SUMS.txt` | SHA-256 checksum of that exact EXE |

The checksum must be regenerated whenever the EXE changes; the build script
does this automatically after verification.

## Publish on GitHub

1. Open the repository's **Releases** page and choose **Draft a new release**.
2. Select or create an unused version tag, such as `v0.1`, pointing to the
   commit used to build the executable.
3. Use a descriptive title, such as **AGtest-framework v0.1 — Windows x64**.
4. Attach the EXE and checksum from `dist/` as release assets.
5. Add release notes, using the template below, and publish when ready.

The README links to the Releases page, where users can find the executable
under **Assets**. GitHub's automatically generated source archives do not
include the EXE.

## Release notes template

```markdown
## Download and run

Download **AGtest-framework.exe** from **Assets** below.
Requires Windows x64. Python and pip are not required.
Put the EXE in your experiments folder and double-click it.

## Results

The application creates these folders beside the EXE when saving results:
- `metrics_tables` — metric histories in XLSX format.
- `solution_tables` — nondominated solutions in XLSX format.

## Verification

The build script runs the project tests and an EXE self-test covering the GUI,
problem factories, reference fronts, short algorithm runs, parallel evaluation,
and XLSX export. `SHA256SUMS.txt` contains the executable's checksum.

## Changes

Describe the changes included in this version.
```

## Repository contents

Keep `src/` (including the required `.pf` reference fronts), `tests/`, `docs/`,
`figures/`, `scripts/`, `README.md`, `LICENSE`, `pyproject.toml`, `run_gui.py`,
`AGtest-framework.spec`, `build_exe.ps1`, and `.gitignore` in Git.

Generated EXEs, `build/`, `dist/`, virtual environments, Python/test caches,
local editor/tool settings, and experiment output folders are ignored. Removing
previously tracked cache files from the index takes effect on GitHub after the
cleanup commit is pushed; it does not remove them from older commits.
