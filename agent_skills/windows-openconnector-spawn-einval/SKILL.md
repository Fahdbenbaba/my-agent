---
name: windows-openconnector-spawn-einval
description: |
  Use when the OpenConnector local development launcher fails on Windows with
  Node.js `spawn EINVAL`, especially while a wrapper is spawning an npm/.cmd
  child process. Prefer the verified direct API runtime when available.
author: My Agent
version: 1.0.0
date: 2026-08-30
---

# Windows OpenConnector `spawn EINVAL`

## Problem

On Windows, the OpenConnector development wrapper failed with Node.js `spawn EINVAL` while starting its child process. The failure occurred with Node.js 24.16.0.

## Context / Trigger Conditions

- Windows local development environment
- OpenConnector repository
- `npm run dev` fails with `Error: spawn EINVAL`
- Failure originates from the local development launcher spawning a child process

## Solution

Run the OpenConnector API entrypoint directly instead of the wrapper that spawns the npm workspace process:

```text
npm run dev:api
```

This starts the API server directly and avoids the failing child-process launcher path.

## Verification

The direct API runtime started successfully and reported:

```text
INFO: connect server listening
url: "http://127.0.0.1:3000"
```

All SQLite migrations completed successfully before the server began listening.

## Evidence

Verified during local setup on 2026-08-30: `npm run dev` failed with `spawn EINVAL`, while `npm run dev:api` completed migrations and listened on `127.0.0.1:3000`.

## Notes

Keep this workaround specific to the Windows/Node process-launch scenario. Re-verify when the OpenConnector launcher, Node.js version, or local runtime changes.
