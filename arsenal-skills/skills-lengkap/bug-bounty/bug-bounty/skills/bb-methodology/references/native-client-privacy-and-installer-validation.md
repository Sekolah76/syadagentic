# Native-client privacy and privileged-installer validation

Use for VPNs, desktop agents, system daemons, split-tunnel helpers, local proxies, and installers that cross an unprivileged-to-root boundary.

## 1. Pin current, meaningful revisions

Test at least:

1. current stable release;
2. newest publicly distributed beta/nightly when policy allows;
3. current development branch for fix/duplicate comparison.

A repository `HEAD` alone is insufficient. Confirm which installer/binary the first-party download page currently directs users to, then inspect the actual release asset. Record commit/tag provenance. For final verification, fetch the asset again, verify its published archive checksum, hash the extracted executable, and confirm the tested executable is byte-identical to the fresh extraction. Run the decisive PoC against that untouched executable—not only a locally compiled binary. Never rely on an old checkout when old versions are excluded.

## 2. Hunt policy/value granularity mismatches

High-signal pattern:

```text
many candidates -> one aggregate security decision -> original candidates reused
```

Examples:

- DNS returns several addresses; `any(excluded)` marks the entire set direct.
- One trusted redirect or certificate downgrades every fallback.
- One split-tunnel match causes unrelated endpoints/processes to bypass protection.

Trace all four stages:

1. candidate generation/resolution;
2. policy decision (`any`, `all`, first, fallback);
3. whether candidates are filtered/partitioned after policy;
4. final per-candidate connection or privileged sink.

A unit test proving the aggregate decision is only a lead. Do not call it a privacy bypass until the final socket/interface/path is observed.

## 3. Build a deterministic network-path oracle

For Linux route/privacy findings, prefer an isolated namespace harness over production traffic:

1. Build the real target binary.
2. Create two network namespaces/listeners representing tunnel and direct paths.
3. Route ordinary traffic to the tunnel listener.
4. Add a policy rule mapping the product's real `fwmark` to the direct listener.
5. Supply controlled mixed resolution locally (`/etc/hosts` is enough when the application uses system resolution).
6. Send a real application-protocol request, e.g. SOCKS5 domain CONNECT.
7. Capture both the program's route decision and which listener received the connection.
8. Run a control connection to prove the same endpoint normally uses the tunnel.
9. Cleanup routes, rules, namespaces, hosts-file entries, and child processes in `finally`/`trap`.

Required proof shape:

```text
control=<tunnel listener>
poc=<direct listener>
decision=<mixed candidates + direct decision>
RESULT=confirmed
```

Use documentation promises as intent evidence only after technical proof. To answer “by design,” separate the intended authorized action from the observed authority expansion: an excluded destination may intentionally bypass the tunnel; a non-excluded sibling inheriting that bypass is a different claim. Corroborate intent with UI guarantees, design docs, changelogs, and especially prior fixes that call the same boundary crossing a leak. Beta labeling lowers confidence/priority, not the need for correct boundary enforcement.

## 4. Audit installer ownership to privileged execution

Search installers for root-path writes with caller-derived ownership:

```bash
install -o "$(id -u)" -g "$(id -g)" ... /usr/bin/...
chown "$USER" ... /usr/lib/... /opt/...
```

Then prove a complete chain:

1. destination is a privileged/system path;
2. ordinary user remains owner or writer after installation;
3. systemd/root daemon/updater later executes or loads it;
4. no integrity or ownership check occurs before use;
5. the vulnerable path is currently distributed or recommended.

Safe reproducer: mirror the exact `install` command under a temporary prefix, modify the installed file without sudo, then execute it through a controlled privileged launcher and verify a root-owned marker. Do not overwrite real `/usr/bin` files.

For “by design” rebuttal, distinguish benign per-user ownership from privileged execution. User ownership may be intentional for a desktop AppImage; it is still unsafe for a system-path executable later run by a root service. Confirm the shipped unit has no `User=`/`DynamicUser=` restriction and inspect the distributed installer asset itself, not only repository source. State the honest prerequisite: attacker already has local code execution as the installing user, but needs no later sudo credential.

Check both the primary daemon and adjacent helpers/plugins: a root daemon may locate helpers relative to `current_exe()` and execute a user-writable sibling on demand.

## 5. Shared system-daemon authorization

A world-connectable socket can be intentional if Polkit/peer credentials authenticate callers. The real question is authorization granularity after authentication.

For cross-user leads, verify in a disposable two-user VM:

- user A stores secret/account/process state in the system-wide daemon;
- user B authenticates only as user B;
- user B invokes a sensitive RPC against A's state;
- daemon binds the request to neither peer UID nor resource owner.

Source confidence is not enough for submission when active/inactive Polkit behavior or desktop-session state may change reachability. Runtime two-user proof required.

## 6. Falsification and report gates

Before drafting:

- Run the reproducer repeatedly on stable and development revisions.
- Search public issues/PRs/commits using root-cause terms, not just the proposed title.
- Confirm no later per-candidate validation, filtering, signature, ownership, or firewall correction exists.
- Separate confirmed findings from high-confidence leads awaiting environment-specific proof.
- Attach scripts as `.txt` if the program requires non-executable artifacts.
- Keep production source unchanged; preserve minimal regression patches separately for each revision if line context differs.
- If the user requests one combined report plus ZIP, follow `references/security-submission-bundle.md`: re-run PoCs from staged paths, include evidence and checksums, secret-scan, CRC-test, exact-member-check, then deliver one archive.

## Common pitfalls

- Claiming interface leakage from a routing enum alone.
- Assuming DNS answer order is stable; prove fallback still remains under the downgraded route.
- Treating authentication as resource authorization in a multi-user system daemon.
- Auditing repository code but not the release asset first-party documentation actually distributes.
- Reporting helper ownership without proving a privileged execution sink.
