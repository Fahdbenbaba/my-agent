---
name: windows-node-spawn-einval
description: |
  Workaround for the verified OpenConnector local-development spawn EINVAL issue on Windows.
author: My Agent
version: 1.0.0
date: 2026-08-30
---

# Windows Node child-process spawn EINVAL workaround

## Problem

The OpenConnector local development wrapper failed on Windows with `spawn EINVAL` while starting its child process.

## Context / Trigger Conditions

- Windows development environment
- Node.js child-process launcher
- OpenConnector `npm run dev`
- `spawn EINVAL`

## Solution

Use the direct OpenConnector API entrypoint `npm run dev:api` instead of the development wrapper that failed during child-process spawning.

## Verification

The direct API runtime started successfully and listened on `http://127.0.0.1:3000`.

## Evidence

Verified during the local OpenConnector setup session on 2026-08-30: the wrapper produced `spawn EINVAL`, while `npm run dev:api` completed database migrations and started the server on port 3000.

## Notes

This workaround is environment-specific. Re-verify against the installed Node.js version and project scripts before applying it elsewhere.
