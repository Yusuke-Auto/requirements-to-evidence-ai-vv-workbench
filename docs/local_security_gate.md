# Local Agent / Network / Repository Security Gates

Date: 2026-10-25. Scope: synthetic V&V repo only. **No real secret, private employer data, mail or customer records** are needed. This is an execution checklist, not evidence that the user's actual machine has passed.

## Gate 0: native Windows permission check (15 minutes; no WSL required)

Claude Code runs on native Windows; built-in OS shell sandboxing does **not**. For a small synthetic and human-supervised project, test Claude's built-in Read permission denial **without claiming subprocess isolation**. Keep default/manual permission mode and avoid untrusted or unattended shell commands.

Use Windows PowerShell in a standalone temporary directory (not System32 and not a personal/work repository):

```powershell
$testDir = Join-Path $env:TEMP 'life462-permission-test'
New-Item -ItemType Directory -Force (Join-Path $testDir '.claude') | Out-Null
Set-Location $testDir
Set-Content -Path 'public.txt' -Value 'LIFE462_PUBLIC=OK'
Set-Content -Path '.env' -Value 'SYNTHETIC_ONLY=NOT_A_REAL_SECRET'
@'
{
  "permissions": {
    "defaultMode": "default",
    "deny": ["Read(./.env)", "Edit(./.env)"]
  }
}
'@ | Set-Content -Path '.claude/settings.local.json' -Encoding UTF8
claude.cmd
```

Inside Claude Code inspect `/permissions` to confirm the local deny rules loaded. Ask it to call its **Read tool only**, once on `public.txt` and once on `.env`. Do not allow it to use shell/PowerShell/Python/MCP or alternate tools, and do not print file contents. Expected: public read allowed, dotenv **tool denied by policy**, no fallback. Screenshot or redacted tool result is execution evidence; an AI's statement without the tool call is insufficient.

If the deny rule is ignored, Gate 0 FAIL. Do not claim this blocks arbitrary subprocesses or network egress on native Windows: file-tool permissions are an application-level guard, not an OS security boundary.

## Gate 1: optional WSL2 OS-enforced isolation (30 minutes)

1. Record the environment without exposing private values:
   - In Windows PowerShell: `wsl --status` and `claude --version`.
   - In WSL2: `uname -s`, `command -v bwrap`, `command -v socat`, `claude --version`.
   - Do not install missing dependencies merely to finish this gate. If WSL2, bubblewrap or socat is unavailable, result = BLOCKED; use an isolated container or set it up in a separate explicitly approved change.
2. On **WSL2 only**, merge the following into *user-level* `~/.claude/settings.json`, preserving unrelated keys and backing up the existing file:
   
   ```json
   {
     "sandbox": {
       "enabled": true,
       "failIfUnavailable": true,
       "allowUnsandboxedCommands": false,
       "network": {
         "strictAllowlist": true,
         "allowedDomains": []
       }
     }
   }
   ```

   This is an example of the required **user** setting; do not paste over existing configuration or put this into this repository's `.claude/settings.json`. For this offline demo zero destinations are needed. On native Windows the Claude Code Bash sandbox is unsupported; applying `failIfUnavailable` will block Claude Code startup. Moving execution to WSL2/container is preferable to weakening the setting. Work in a clone under the WSL2 home directory, not in a parent folder containing private records.
3. Start Claude from this repository; inspect the **resolved** `/sandbox` and `/permissions`. Confirm that actual shell sandboxing is ON, unsandboxed fallback OFF, user-scope `strictAllowlist` ON, and project `Read(.env)` + filesystem deny rules loaded. Confirm no unexpected added directories/allow rules. If settings are ignored, stop.
4. Build a local synthetic fixture, with no credentials:
   
   ```sh
   printf 'SYNTHETIC_ONLY=NOT_A_REAL_SECRET\n' > .env
   ```

   Ask Claude Code to read `.env` **using its Read tool**, not to paste the contents. The tool must **deny**. Then ask Claude Code to read it using a **sandboxed shell command**. It must also **deny**. If either succeeds, Gate 1 FAIL. If the command runs unsandboxed or only displays a prompt, mark INCONCLUSIVE and deny the prompt. `.env` is already gitignored.
5. Preserve only timestamp, tool type, result (DENY/PASS/FAIL), Claude version and a redacted error category. No fixture content or settings secrets in Jira.

Why both tests: Claude Code's shell sandbox does not constrain built-in Read, hooks or MCP tools. The project Read rules and sandbox file rules protect different pathways.

## Gate 2: MCP/connector grants and egress policy (20 minutes)

**Native Windows, no OS shell sandbox:** The app-level Read denial demonstrated in Gate 0 does **not** enforce outbound network restrictions or stop arbitrary subprocesses from reading files. Record this as **accepted only for attended, synthetic-data tasks**, not as a tested network denial. Do not run `curl` on Windows and call a regular HTTP or DNS failure a sandbox-negative-test PASS.

1. From a normal PowerShell terminal in the **actual project directory**, inspect configured Claude Code MCP servers (read-only):
   ```powershell
   claude.cmd mcp list
   ```
   Then in Claude Code, use `/mcp` to inspect tool access and server status. MCP servers can be at local, project, user or managed scope. Do **not** paste raw output from `claude mcp get`, `.mcp.json`, `~/.claude.json`, environment variable dumps or credential files into Jira/ChatGPT. Inspect first and share only **redacted server names, enabled/disabled state, read/write capabilities, scope**. URL query strings, headers, auth tokens, user identifiers and client secrets must be removed.
2. For each server: classify provider, tool capabilities (read / write / external send / destructive), account scope, necessity for synthetic portfolio development, user-approval path, and whether the server is trusted. Unknown or unneeded services: disconnect/disable after user approval. Account permissions are administered separately from this GitHub PR.
3. Native Windows minimum policy: no unattended network-active shell commands, no real credentials/business records in CLI agent context, no implicit `Yes and don't ask again` for network/upload commands. Require explicit approval for **destination, action, data classification and reversibility** before any external send. An interactive approval is procedural, not a verified egress firewall.
4. For an OS-enforced **network-deny negative test**, first run the agent inside an explicitly approved WSL2 shell sandbox/VM/container with an actual fail-closed proxy and allowlist. Check effective `strictAllowlist` from USER/managed settings and sandbox=ON. Only there, invoke via **sandboxed shell**:
   ```sh
   curl --head --max-time 7 https://example.com
   ```
   A policy-level host-not-allowed denial is PASS. Successful HTTP is FAIL; DNS timeout, generic network error or a permission prompt is INCONCLUSIVE. Do not retry unsandboxed. This tests subprocess egress only, not MCP/WebFetch or cloud-connected tools.
5. All evidence is metadata only: source, date, capability, expected/actual DENY or UNKNOWN; never copy token values.

## Gate 3: GitHub settings (10 minutes)

1. Open GitHub repository -> Settings -> Branches. For `main`, add a branch protection rule:
   - Require a pull request before merging.
   - Require status checks before merging: select existing **offline-vv** job from workflow `verify`.
   - Block force pushes and deletions; apply to administrators where available.
   - Optional: require **one approving review only if another authorized reviewer exists**. On a solo personal repository, requiring external approval without a reviewer will indefinitely block merges. Use human inspection + required CI as a practicable minimum until a reviewer is available.
2. Repository -> Settings -> Actions -> General -> Workflow permissions: set **Read repository contents and packages permissions** and turn off **Allow GitHub Actions to create and approve pull requests**. This supplements (does not replace) the workflow's `permissions: contents: read` and `persist-credentials: false`.
3. Confirm the branch metadata changes from `protected=false` to `true` and required CI remains green. Inspect PR #1, then make an explicit human merge decision. Do not automatically merge a PR because a CI test passed.

## Completion evidence to write back

For each gate capture: **Before / Change / After / command or screen / expected / actual / PASS-FAIL-INCONCLUSIVE / risk**. For the native Windows baseline, require a verified application-level denied Read test plus documented acceptance of unsandboxed subprocess / egress risk; connector inventory, branch protection and PR disposition still need verified evidence. For the stronger OS-sandbox tier, additionally require actual sandboxed shell denied-read and denied-egress tests in WSL2 or a VM/container. Do not mislabel one tier's result as the other.

References:
- https://code.claude.com/docs/en/sandboxing
- https://code.claude.com/docs/en/permissions
- https://code.claude.com/docs/en/settings
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/managing-a-branch-protection-rule
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository
