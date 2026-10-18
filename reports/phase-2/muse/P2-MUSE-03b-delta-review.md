# Muse delta review on 03b (relayed by Ashish, 2026-10-18 05:23 UTC)

Verbatim:

> Read it as a delta against my 03b findings. Short version: R3B-1 and R3B-3 are properly closed, R3B-2 is still open, R3B-4 needs evidence I can actually see.
>
> * R3B-1 (home-folder writes): closed in design. Sandbox write-scoped to project+temp, denyWrite on `~/.ssh`/`~/.aws`/`~/.gnupg`/LaunchAgents, Edit denies on the rc files. One residual worth a live test: since `Write(...)` permission rules never match, creating a new file at a sensitive path via the Write tool isn't denied — it would only prompt. Confirm what actually happens with a Write to `~/.ssh/authorized_keys`.
> * R3B-2 (gh/gcloud/netrc gaps): not addressed in this version. No mention of `~/.config/gh` anywhere. The empty-allowlist network helps — a stolen token can't leave without a prompt — but the token would still be visible to the cloud model the moment it's read. Still recommend the permission denies; cheap to add.
> * R3B-3 (env vars): closed. `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB=1` (allowlist-style, not a name list) plus dropping PyPI from pre-allowed hosts kills both the visibility problem and my `twine upload` exfil chain. Residual: run one sandboxed `printenv` to see which vars actually survive the scrub.
> * R3B-4 (destructive tests): claimed but not evidenced. You cite `test-results/live/` — those files aren't in front of me, so I can't verify. The "writes only to project+temp" claim is exactly what those tests need to prove. Paste the key excerpts and I'll check them.
>
> Two new observations. First, the `Write(...)` vs `Edit(...)` quirk is a genuinely valuable find — it means "deny writes" can never be fully expressed through permissions.deny, which makes the sandbox write-scoping the real control, not a backup. That belongs in the threat model permanently. Second, the memory-poisoning scan is a good addition, and the "(pattern-based: a reworded line can pass)" honesty is exactly the right register.
> Overall: the boundary is now in good shape — what remains is verification, not redesign. If you paste `test-results/live/`, I'll verify the test claims; if you want a formal 03c packet for the repo, say the word.

## What was done (commit be08e43)

- R3B-2: denies added for 8 CLI credential locations (settings, sandbox, guard) and live-tested.
- R3B-1 residual: Write to `~/.ssh/authorized_keys` denied by permission settings, with and without hooks.
- R3B-3 residual: sandboxed `printenv` names recorded; no key/token names survive.
- R3B-4: verbatim excerpts in P2-MUSE-03c-review-request.md.
- Note: 03c content already exists. Muse's review of TASK-0014 (P3-MUSE-04) is still outstanding.
