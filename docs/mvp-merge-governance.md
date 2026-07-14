# MVP Merge Governance Administrator Checklist

Configure the repository before declaring issue #24 complete:

1. Protect `main`.
2. Require the GitHub Actions workflow `CI` before merge.
3. Require these checks specifically:
   - `Static quality`
   - `MVP unit and integration tests`
   - `Golden MVP acceptance`
   - `Package verification`
4. Block merge when required checks fail.
5. Require branches to be up to date before merge.
6. Restrict direct pushes to `main` where the repository plan supports it.
7. Require at least one human approval for MVP release changes.
8. Do not grant Slugger automation permission to approve, merge, or publish releases.
9. Store real Codex and GitHub sandbox credentials only in protected environments or repository secrets unavailable to untrusted pull requests.
10. Run the manual protected integration workflow before closing issue #24.
