# Memory Protocol v1

## Purpose
Capture durable user context without requiring explicit “remember this” commands, while preventing AI inference from silently becoming fact.

## Memory Check
Every meaningful assistant turn MUST evaluate:
- Did the user state a durable fact about themselves, their environment or a recurring constraint?
- Did the user express a stable preference or a change to one?
- Was a decision made?
- Did a project materially progress?
- Is there a new open loop that future assistants should know?
- Did the user correct an earlier AI assumption? If yes, use the Correction Protocol.
- Is this merely transient chatter or model inference? If yes, do not promote it to canonical memory.

## Priority model
1. User correction
2. Explicit user decision or instruction
3. Explicit user fact
4. Repeated user pattern supported by multiple interactions
5. AI inference — candidate only; never canonical by itself

## Event model
Canonical memory is append-oriented. Create a new file in `10_Memory/Events/` using schema `pmo.memory-event/v1`. Do not rewrite a large global memory file as the source of truth.

Required fields: `id`, `type`, `created_at`, `source`, `importance`, `confidence`, `explicitness`, `status`.

Use `supersedes` when the user explicitly changes a prior fact/preference/decision. Preserve history rather than deleting the old event.

## Promotion guidance
Save explicit decisions and corrections immediately. Save durable explicit facts when likely useful in future interactions. Save inferred patterns only when confidence is high enough for the configured threshold and mark `explicitness: inferred`.
