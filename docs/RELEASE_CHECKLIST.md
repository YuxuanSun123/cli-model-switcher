# Release Checklist

Use this checklist when preparing a tagged GitHub release.

## v0.4.0

1. Confirm the local tree is clean:

   ```bash
   git status --short --branch
   ```

2. Run local validation:

   ```bash
   python scripts/validate_skill.py .
   python scripts/cli_model_switcher.py lite --dry-run --json
   python scripts/cli_model_switcher.py lite --all-common --dry-run --json
   python scripts/cli_model_switcher.py setup --lite --dry-run --no-install
   python scripts/cli_model_switcher.py secret audit --scope all --fail
   ```

3. Push `main` when ready:

   ```bash
   git push origin main
   ```

4. Create and push the release tag:

   ```bash
   git tag -a v0.4.0 -m "v0.4.0"
   git push origin v0.4.0
   ```

5. Confirm the GitHub Release workflow completed and generated notes from `CHANGELOG.md`.

6. Smoke test install commands from the release:

   ```bash
   sh install.sh --lite --dry-run
   ```

   ```powershell
   .\install.ps1 -Lite -DryRun
   ```
