# AI Development Security Baseline v0.1

This repository contains a **synthetic, public-safe** V&V demo. These are the intended default boundaries, not an assertion that a developer workstation or external account has already been hardened.

## Asset and execution boundaries

| Surface | Execution and access | Boundary status |
| --- | --- | --- |
| Cloud chat, planner and connected tools | Cloud; explicit user-granted issues, calendars, email, Drive and repository scopes | Enumerate and review real connector grants; do not assume shell sandbox limits them |
| Claude Code or other agent CLI | Developer machine, terminal/PowerShell, WSL2 or disposable container | Agent permissions and an OS-enforced sandbox are separate; local settings are unverified |
| IDE / extensions | Developer workstation, project folder, terminals and tasks | Use Workspace Trust Restricted Mode for unknown code; explicitly review extensions and MCP servers |
| Scripts / package managers | Local machine or temporary workspace | Prefer offline and synthetic execution; dependency installation requires human approval |
| GitHub Actions | Hosted runner, repository checkout, job token | Workflow-level `contents: read`, no persisted checkout token; repository settings still need verification |

Data flow: synthetic requirement -> planner draft -> approved scoped execution -> deterministic tests -> CI results -> human review -> optional authorized external write. Untrusted files, logs, pages and tool responses must never grant authority.

## Guardrails

1. **Sandbox.** Run unknown code and AI-proposed shell commands inside a disposable workspace/container. On Windows, Claude Code's Bash sandbox is supported via WSL2 rather than native Windows. On a supported platform, enable sandboxing, require fail-closed if unavailable, and disable unsandboxed fallback. Inspect resolved state with `/sandbox` and test a blocked file read; prompts alone are not OS isolation.
2. **Least privilege.** Default agent rights to reading this repository and writing only its intended output/test paths. No broad home directory, other workspace, employer material, cloud production resource or elevated shell authority. Use the default/manual permission mode and review each permission in `/permissions`. Treat new MCP/connector tools as new authority.
3. **Secret isolation.** Never paste actual tokens, private keys, unredacted records, or real business/customer data into agent context or public repositories. Use a credential store or process-scoped injection only for tasks with explicit need and human approval; redact logs. Only `.env.example` may be committed with placeholder values. The repository scan now covers `.env` and `.env.*` if present, but the scan is **not** a substitute for proper secret isolation or a comprehensive secret scanner.
4. **Egress.** Offline is the default for repeatable tests. Each model/API call, upload, package download and newly requested destination requires a reviewed purpose, destination and data classification. On supporting Claude Code versions, enforce a strict network allowlist from user/managed settings; a project-only `strictAllowlist` does not enforce it. Sandboxed shell network rules do not automatically constrain cloud connectors.
5. **Destructive action.** No deletions, force pushes, broad file rewrites, secret access, installations, dependency updates, external uploads, deployments or permission changes without explicit human approval of exact target, risk, rollback and audit. Missing approval, ambiguous target or unknown authority => deny.
6. **CI.** Use read-only `GITHUB_TOKEN` unless a single job needs a specifically reviewed elevated scope; avoid long-lived PATs. `actions/checkout` uses `persist-credentials: false`. This workflow executes synthetic offline checks on GitHub-hosted runners and requires no cloud credentials. Verify branch protection, default Actions permissions and PR review rules separately; workflow YAML does not attest to repository-level enforcement.
7. **Audit.** Record action identity, approved authority, artifact/commit, commands and tool calls, timestamps, CI run, negative-test outcome and any rejected egress attempt. Never store the underlying token or confidential payload in logs.

## Tool action classes

- AUTO: read synthetic docs, analyze, propose diffs, run offline tests in constrained workspaces, create local scratch output.
- APPROVE: source edits and PR preparation; scoped reversible issue/calendar changes consistent with user-granted authority.
- STRICT APPROVE: external email/publication, uploading data, installs, secret injection, granting new permissions, CI deployment, merging to a protected branch, destructive writes.
- PROHIBITED: approval bypass, silent privilege escalation, unknown external recipients, actions beyond the user's authorization.

## Negative test

```bash
python -m unittest discover -s tests -p 'test_public_safety_negative.py' -v
python scripts/public_safety_check.py
```

Both negative tests use fabricated key-shaped strings in temporary directories. The checker must fail with an error exit code and avoid echoing the synthetic key. An executable scan only demonstrates the tested detection logic; it does **not** prove agent sandboxing, blocked network egress, local credential isolation, or all possible leak patterns.

## Remaining verification gates (use existing engineering integration session)

1. **Local host gate:** Capture actual CLI/IDE version and `/sandbox`, `/permissions`, Workspace Trust, Windows-vs-WSL2 context; test one blocked read in the real sandbox without using any real credentials.
2. **Egress/connector gate:** Inventory grants and allowlisted domains, then safely confirm one outbound denial using synthetic data, distinguishing local shell from cloud connectors.
3. **CI account gate:** Inspect GitHub Settings -> Actions and branch/ruleset protection with suitable access, confirm PR CI completes, and review the diff before merge.

Never treat a connection error or lack of API privileges as proof that a security setting is absent. This baseline is versioned and should be revised only when there is new evidence.
