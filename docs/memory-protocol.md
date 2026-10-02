# Memory model

## Memory event

A memory event records one durable proposition with provenance, confidence, importance and lifecycle state. History is preserved through `supersedes`, not destructive rewriting.

## Correction event

Correction events represent user-asserted fixes to AI understanding. They are a distinct type because a normal semantic search ranking is not enough: assistants must read corrections before ordinary memory.

## Inference boundary

An AI may detect a possible pattern, but inferred data cannot silently become equivalent to an explicit user statement. Inferred events must be marked, carry confidence, and meet configured thresholds to appear in generated memory views.

## Daily/session record

Daily files answer “what did we do?” rather than “what is true about the user?” Long-term memory and daily activity are deliberately separate.
