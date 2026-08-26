---
name: attack-chain-web2
description: Web2 attack chain plugin — apply Web2 trust boundaries and composition rules on top of attack-chaining-core for authorized testing of web apps, APIs, identity, cloud, and internal services.
version: 1.0.0
---

# Web2 Attack Chain Plugin

## Purpose

Apply Web2-specific trust boundaries and composition rules on top of `attack-chaining-core` for authorized testing of web applications, APIs, identity systems, cloud deployments, and internal services.

Always run the core procedure first. This plugin supplies domain semantics; it does not waive evidence requirements.

## Primary Web2 chain surfaces

- authentication, registration, recovery, MFA, SSO, OAuth/OIDC, and session lifecycle;
- object- and function-level authorization;
- multi-tenant boundaries;
- file upload, parsing, storage, and delivery;
- SSRF and internal service reachability;
- cloud metadata, IAM, secrets, queues, and storage;
- web cache, proxy, host/routing, and request interpretation differences;
- injection primitives and server-side execution;
- client-side execution combined with account/session impact;
- business-logic state machines and race conditions.

## Web2 capability rules

### Identity and session

Do not treat these as equivalent without proof:

- knowing an email address;
- knowing a user ID;
- obtaining a reset token;
- setting a session cookie;
- obtaining an authenticated session;
- bypassing MFA;
- impersonating an administrator.

Check token purpose, audience, expiry, one-time use, binding, rotation, SameSite/domain/path, device/session binding, and revocation.

### Authorization

For IDOR/BOLA chains prove that the identifier from one step can be used against the exact object/action in the next step. Check tenant scoping, indirect references, ownership revalidation, and backend service authorization.

### SSRF and cloud pivots

Separate:

- outbound request confirmed;
- internal host reachable;
- response readable;
- headers/method controllable;
- metadata protections bypassed;
- credentials obtained;
- credentials valid for a specific principal;
- IAM permission allows a protected action.

A blind SSRF is not automatically cloud compromise.

### File chains

Track file bytes, content type, extension, storage key, transformation, execution context, and delivery origin. Upload alone is not execution. Parsing bugs must establish attacker-controlled content reaching the vulnerable parser in a relevant profile.

### Client-to-server chains

XSS or open redirect does not automatically imply account takeover. Establish victim requirements, cookie accessibility, CSRF protections, token exposure, privileged actions, and practical delivery.

### Cache/proxy/request-smuggling chains

Prove front-end/back-end interpretation mismatch in the actual deployment and show how the poisoned or desynchronized request reaches a protected victim or route. Local parser disagreement alone is insufficient.

## Common valid composition patterns

Use only as hypotheses:

- information disclosure -> credential/token acquisition -> authenticated action;
- account enumeration -> recovery weakness -> session acquisition;
- low-privilege write -> stored client execution -> privileged action;
- SSRF -> internal discovery -> secret acquisition -> IAM-authorized impact;
- path/canonicalization mismatch -> authorization bypass -> protected object access;
- upload primitive -> server-side parser/handler -> execution or data access;
- cache poisoning -> victim request influence -> account/data impact;
- race/business-logic flaw -> invariant bypass -> unauthorized value/state change.

## Web2 chain blockers

Explicitly test:

- token audience and nonce mismatch;
- cookies inaccessible to script;
- reauthentication/MFA before sensitive actions;
- backend authorization independent of UI;
- tenant ID derived from trusted identity;
- egress filtering and metadata protections;
- short-lived or non-exportable credentials;
- upload re-encoding and isolated delivery domains;
- CSP and browser behavior;
- proxy normalization;
- idempotency and transaction locking;
- rate limits and fraud controls.

## Required output additions

Include:

- identity and tenant context per step;
- session/token lifecycle table;
- trust-boundary crossings;
- victim interaction requirements;
- cloud/IAM principal and exact permissions when applicable;
- browser/proxy/backend assumptions;
- safe reproduction plan using owned accounts and synthetic data.
