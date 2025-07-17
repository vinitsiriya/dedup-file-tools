# Auditable Agent Bootstrap: From AGENTS.md to Advanced Protocols – A Beginner-Friendly Guide

## What is AGENTS.md?

If you’re new to this project, you might notice a file called `AGENTS.md` at the root of the repository. This file is the starting point for anyone—human or AI—who wants to understand how agents (automated tools or people) should work together on this project.

Originally, `AGENTS.md` was a simple document listing basic rules and steps for agents to follow. It helped ensure everyone started with the same information and followed the same process. Over time, as the project grew and more complex workflows were needed, the protocols described in `AGENTS.md` evolved into a more advanced, auditable system.

## Why Did We Need Something More?

As projects get bigger, it’s easy for important steps to be missed, for agents to work with outdated information, or for mistakes to go unnoticed. The original `AGENTS.md` was a great start, but it wasn’t enough to guarantee reliability, traceability, and smooth collaboration—especially when both humans and AI are involved.

## The Evolution: From Simple Rules to Auditable Protocols

To solve these problems, the project introduced the **Auditable Agent Bootstrap** protocol. This is a set of clear, step-by-step rules and scripts that every agent must follow when starting or resuming work. The protocols are now split into dedicated, versioned files (see `agents/rules/protocol.md` and related docs), making them easier to update, audit, and enforce.

## How Does the Auditable Agent Bootstrap Work?

1. **Start with AGENTS.md:** This file now acts as an index, pointing you to the latest protocols and rules.
2. **Directory Inspection:** Before doing anything, agents must scan the project directory (ignoring files like `.venv`, `.git`, etc.) to get a real-time map of all files. This ensures no one works with stale or missing data.
3. **Follow agent-bootstrap.md:** Agents read and follow the instructions in `agent-bootstrap.md` step by step, making sure all setup and requirements are met.
4. **Use Scripts, Not Manual Steps:** Important actions (like archiving or resuming work) are done using scripts, so everything is consistent and logged.
5. **Centralized, Versioned Protocols:** All rules are kept in dedicated files, so updates are easy and everyone is always on the same page.

## Why Is This Better?

- **Reliability:** Agents always work with the latest, complete project state.
- **Auditability:** Every action is logged and can be checked later.
- **Maintainability:** Protocols are easy to update and enforce.
- **Collaboration:** Both humans and AI can follow the same clear steps, making handoff and teamwork simple.

## Quick Comparison

| Feature                        | Auditable Agent Bootstrap | Old/Standard Startup   |
|-------------------------------|:------------------------:|:---------------------:|
| Directory Inspection           | Required, every resume   | Rarely, if ever       |
| Stepwise Bootstrap             | Scripted, enforced       | Often ad hoc          |
| Protocol/Rule Centralization   | Modular, versioned files | Scattered, in code    |
| Auditing & Traceability        | Script/log driven        | Minimal               |
| Human-Agent Collaboration      | First-class              | Siloed                |

## Where to Learn More

- Start with `AGENTS.md` for the index and overview.
- See `agents/rules/protocol.md` for the full agent protocol.
- Check `agents/workflow/agent-bootstrap.md` and `agents/workflow/workflow-protocol.md` for workflow and collaboration details.

---

*By following the Auditable Agent Bootstrap protocol, you’ll help keep the project reliable, auditable, and easy for anyone—human or AI—to join and contribute!*

---

# Auditable Agent Bootstrap: A Modern Protocol for Reliable AI and Human Collaboration

## Introduction

As AI agents become more integrated into complex software projects, the need for robust, auditable, and collaborative startup protocols has never been greater. Traditional agent startup methods often rely on static entry points, implicit assumptions, and minimal auditing—leaving room for errors, missed steps, and poor traceability. In contrast, the "Auditable Agent Bootstrap" method, as implemented in the fs-copy-tool project, sets a new standard for reliability and collaboration.

## What is Auditable Agent Bootstrap?

Auditable Agent Bootstrap is a protocol-driven approach to initializing and resuming agent work in a software project. It is designed to ensure that every agent (human or AI) always operates with a complete, up-to-date understanding of the project state, and that every action is traceable and compliant with project rules.

## Key Features

### 1. Explicit Directory Inspection
Before any work begins, the agent must scan the entire project directory (excluding irrelevant files like `.venv`, `.git`, etc.) to build an accurate, real-time map of the workspace. This eliminates assumptions and ensures the agent never works with stale or incomplete information.

### 2. Stepwise, Scripted Bootstrap
Agents are required to read and execute all `agent-bootstrap.md` instructions, following each step in order. This guarantees that all prerequisites, environment setup, and protocol requirements are satisfied before any further action is taken.

### 3. Modular, Versioned Protocols
Rather than embedding rules in code or scattered docs, all protocols and operational rules are centralized in dedicated, versioned files. This makes it easy to update, audit, and enforce best practices across the team.

### 4. Script-Driven, Auditable Actions
Critical actions—such as archival, setup, and resume—are performed via scripts, not manual steps. This ensures consistency, prevents human error, and creates a clear audit trail for every operation.

### 5. Human + Agent Collaboration
The protocol is designed for both human and AI agents, with clear, repeatable steps and documentation. This enables seamless handoff, midstream recovery, and collaborative workflows.

## Comparison to Standard Methods

| Feature                        | Auditable Agent Bootstrap | Standard Agent Startup |
|-------------------------------|:------------------------:|:---------------------:|
| Directory Inspection           | Required, every resume   | Rarely, if ever       |
| Stepwise Bootstrap             | Scripted, enforced       | Often ad hoc          |
| Protocol/Rule Centralization   | Modular, versioned files | Scattered, in code    |
| Auditing & Traceability        | Script/log driven        | Minimal               |
| Human-Agent Collaboration      | First-class              | Siloed                |

## Benefits
- **Reliability:** Agents never operate on stale or partial state.
- **Auditability:** Every action is logged and reproducible.
- **Maintainability:** Protocols are easy to update and enforce.
- **Collaboration:** Supports both human and AI workflows, with seamless handoff.

## Conclusion

The Auditable Agent Bootstrap method is a best-in-class approach for any project where reliability, auditability, and collaboration are critical. By making every step explicit, script-driven, and protocol-compliant, it ensures that both human and AI agents can work together efficiently, recover from interruptions, and maintain a clean, trustworthy project history.

## Architecture Note (2025-07)
- All job databases are now named `<job-name>.db` in the job directory. All CLI commands require `--job-name`.
- The checksum cache database is always named `checksum-cache.db` in the job directory.

---

*For implementation details and real-world examples, see the fs-copy-tool project’s `AGENTS.md` and related protocol files.*
