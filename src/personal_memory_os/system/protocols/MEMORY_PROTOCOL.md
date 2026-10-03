# Memory Protocol v1

## Purpose

Capture durable user context while keeping the user in control of what becomes canonical memory.

## Default policy

The default PMO configuration is explicit-first:

- explicit “remember this” or equivalent requests are saved;
- explicit decisions may be saved when the user asks to retain them;
- corrections use the Correction Protocol;
- when `memory.auto_save: false`, other potentially useful information is proposed as a concrete save candidate rather than silently stored;
- when `memory.auto_save: true`, eligible durable information may be stored within the configured policy.

Silence is not consent to save.

## Memory Check

On meaningful turns, consider whether the interaction contains:

- a durable user fact or recurring constraint;
- a stable preference or a change to one;
- an explicit decision;
- material project progress;
- an open loop useful to a future assistant;
- a correction of an earlier understanding.

The Memory Check decides whether to save, propose, or do nothing according to Config. It does not override the saving policy.

## Priority model

1. User correction
2. Explicit user decision or instruction
3. Explicit user fact
4. Repeated user pattern supported by multiple interactions
5. AI inference

AI inference must stay distinguishable from explicit user information. Do not silently turn model inference into a user fact.

## Event model

Canonical memory is append-oriented. Create a new file in `10_Memory/Events/` using schema `pmo.memory-event/v1`, starting from `_system/templates/memory-event.md`. Put the memory content in the body after the closing `---`. Do not rewrite a global memory view as the source of truth.

Required fields: `id`, `type`, `created_at`, `source`, `importance`, `confidence`, `explicitness`, `status`.

Use `supersedes` when the user explicitly changes a prior fact, preference or decision. Preserve history rather than deleting the old event.

`memory.inferred_memory_min_confidence` controls whether intentionally created inferred records appear in generated views; it is not permission to auto-create inferred memory.
