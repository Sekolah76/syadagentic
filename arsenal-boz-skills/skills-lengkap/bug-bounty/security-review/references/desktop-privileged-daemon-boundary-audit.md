# Desktop client ↔ privileged daemon boundary audit

Use for VPNs, endpoint agents, desktop updaters, Tauri/Electron shells, system services, root helpers, launch daemons, and Windows services.

## Scope and release discipline

1. Pin the exact latest release tag and commit. Record both.
2. Check worktree status before analysis. Never overwrite, revert, or attribute pre-existing edits to the audit.
3. Trace shipped packaging paths separately: distro package, raw installer, GUI updater, Windows installer, macOS helper installation. A safe package does not make a separate raw installer safe.
4. Keep tests local and disposable. Prefer source-level tests and temporary directories; never probe production.
5. Exclude self-harm, pure DoS, third-party-only CVEs, and patterns absent from the pinned release.

## Surface map

Build one table before chasing sinks:

| Layer | Questions |
|---|---|
| Renderer/webview | Which Tauri commands/plugins/capabilities can untrusted renderer content invoke? |
| GUI backend | Which commands reach the daemon, filesystem, shell, updater, or opener? |
| Daemon transport | UDS, named pipe, XPC, loopback TCP? Path/name, owner, mode/DACL, stale-object handling? |
| Authentication | Peer UID/PID, code signature, token, Polkit action, session cache? What principal is established? |
| Authorization | Does each RPC constrain that principal to its own resources and allowed actions? |
| Privileged sinks | Firewall, routes, DNS, account secrets, cgroups, process launch, file deletion/write, service install/update? |
| Packaging | Who owns every executable later launched by root/SYSTEM? Are service paths and sidecars writable? |

Map every RPC, including hidden CLI commands. GUI exposure is not the complete daemon API.

## Core rule: authenticate, then authorize

A valid local client is not automatically entitled to all daemon state.

For every accepted connection, preserve the authenticated principal—UID/session/PID/signing identity—in transport metadata. At each RPC enforce:

- **resource ownership:** account/session/secret belongs to caller;
- **target ownership:** caller owns target PID/path/object;
- **action scope:** read-only status differs from account export, firewall changes, updater execution, or process routing;
- **multi-user isolation:** a system-wide daemon must not expose one user's state to another valid local user.

Red flags:

- world-connectable socket plus one broad Polkit action;
- `auth_self` for the complete service API;
- code-signature verification treated as authorization for every RPC;
- one connection-level prompt unlocking all later commands;
- peer credentials discarded before handlers;
- global singleton account/session state behind per-user authentication.

A useful proof question: “Can user B authenticate as B, then read or mutate user A’s daemon state?”

## High-value command classes

Prioritize RPCs that:

- export recovery phrases, autologin links, PINs, tokens, keys, seeds, account IDs, or account summaries;
- store/forget accounts, rotate identities, initiate payments, or obtain credentials;
- connect/disconnect tunnels or weaken DNS/firewall/LAN policy;
- add arbitrary PIDs to split-tunnel/cgroup bypasses;
- return privileged log/config paths or delete files;
- launch helper binaries or install updates.

Trace returned “encrypted” blobs together with companion material. Returning ciphertext and its PIN/key in one response is secret export, not protection.

## Arbitrary PID and cross-user process controls

For PID-taking RPCs, verify all of:

1. PID is positive and currently exists.
2. PID owner matches authenticated peer UID/session.
3. Identity is stable across check/use: use pidfd or equivalent where available; otherwise acknowledge PID-reuse TOCTOU.
4. Kernel operation cannot move another user's process into a bypass cgroup/job/filter.
5. The handler propagates errors instead of reporting success after a failed privileged operation.

Impact must be concrete. For VPN split tunneling, moving a victim process into the excluded cgroup can expose subsequent connections outside the VPN. Prove with a two-user disposable VM and a benign repeated public-IP request; avoid intercepting real traffic.

## Installer and privileged-child ownership

Inspect every executable path used by systemd, SCM, launchd, or a privileged `Command::new`/`exec`.

Dangerous pattern:

```sh
sudo install -o "$(id -u)" -g "$(id -g)" -m 755 helper /usr/bin/helper
```

Mode `0755` does not help when the unprivileged owner retains write permission. If root later executes that file, replacement gives root code execution.

Check:

- destination owner/group and mode;
- parent-directory ACLs;
- service `ExecStart` and recovery restart behavior;
- sibling helpers loaded by privileged processes;
- DLL/shared-library/plugin search paths;
- updater staging and replacement paths;
- whether checksums authenticate provenance (a checksum downloaded beside the artifact does not establish publisher trust).

Minimal safe validation: reproduce the exact `install` invocation in a temporary directory, inspect `stat`, then show the owner can overwrite the file. Runtime root execution belongs only in a disposable VM.

## Socket, pipe, and stale-path checks

### Unix sockets

- Parent directory must be root-owned and not writable by untrusted users.
- Prefer restrictive socket mode/group; world writable is acceptable only with robust per-connection authorization.
- Before unlinking a stale path, use `lstat`/type checks and a trusted parent. Avoid generic removal through attacker-controlled parents.
- Capture peer UID/PID immediately; carry it into request context.

### Windows named pipes

- Review DACL independently of client code-signature verification.
- Reject remote clients.
- Verify PID-to-image/signature logic is race resistant; opening/verifying the process should bind to the process object, not only a reusable numeric PID.
- Fail closed if daemon self-signature or verifier initialization fails. “Daemon unsigned, skip all client checks” is unsafe outside explicit development builds.

### XPC

- Set signing requirements before accepting/resuming/forwarding a connection where platform semantics require it.
- Verify requirement includes expected team and designated identifier.
- Do not assume reaching an XPC listener proves authorization for every privileged RPC.

## Tauri and GUI checks

- Enumerate `invoke_handler` commands and plugin capabilities together.
- Flag unrestricted `shell:allow-spawn`, opener path scopes, updater permissions, deep-link handlers, and asset protocol scopes.
- Trace remote/decentralized metadata into `openUrl`, shell args, local asset URLs, and daemon RPCs.
- Renderer compromise is a relevant attacker model only when an attacker-controlled input-to-renderer execution path is proven; do not report hypothetical “if XSS exists” chains as findings.

## File/path and serialization checks

For root-owned data/config/log operations:

- validate fixed base directory, ownership, and mode before use;
- reject symlink/reparse-point targets where writes/deletes cross trust boundaries;
- use no-follow/openat-style primitives for mutable names;
- avoid check-then-open canonicalization races;
- bound protobuf/JSON/TOML/bincode sizes and nesting before expensive decode;
- unsafe deserialization requires a meaningful gadget/type effect; ordinary Serde JSON parsing is not code execution.

## Minimal non-production tests

- **Installer ownership:** exact install command under `mktemp`; `stat`; owner overwrite.
- **Cross-user daemon auth:** two local users in a disposable VM; user A creates state, user B authenticates as B and attempts the sensitive RPC.
- **PID authorization:** user A starts a harmless network loop; user B targets its PID; inspect cgroup membership and new route behavior.
- **Socket permissions:** bind under temporary trusted directory; inspect mode and peer credential propagation.
- **Symlink test:** temporary root-like directory tree with a sentinel target; invoke isolated file helper, never real `/etc`, `/var`, or production paths.
- **Deserializer:** unit-test parser with bounded malformed inputs; assert rejection without filesystem/network side effects.

## Finding gate

Report only when all are present:

1. exact pinned-release `file:line` source;
2. unprivileged attacker-controlled input or principal;
3. complete path to privileged sink or secret;
4. missing mitigation checked explicitly;
5. non-self-harm security impact;
6. minimal safe test.

Use “candidate” when platform runtime behavior still needs disposable-VM confirmation. State confidence honestly. Keep the result to the user’s requested maximum; omit safe-item inventories beyond one coverage line.
