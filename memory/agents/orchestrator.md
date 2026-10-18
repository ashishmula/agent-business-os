---
agent: orchestrator
size_cap: 3KB
---

# Orchestrator memory

Role: assigns tasks, writes the ledger through `./abos`, runs gates, keeps the status board current.

## Lessons
- Muse packets arrive pasted in chat: save them byte-for-byte as files, then `./abos handoff receive`.
- Muse packets so far omit `security_or_privacy_notes` and repo file hashes; intake warns, ask Muse to add them.
- Device folder writes: git commits must run on the Mac itself, not in the sandbox shell.
