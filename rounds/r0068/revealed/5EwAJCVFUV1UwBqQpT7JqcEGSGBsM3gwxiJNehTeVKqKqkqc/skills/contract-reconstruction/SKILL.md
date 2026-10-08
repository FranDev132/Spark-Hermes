---
name: contract-reconstruction
description: Recover missing or rewritten behavior and linked defects from callers, protocols and surviving tests when a small local correction does not explain every symptom.
---

# Recover obligations before rebuilding behavior

Use this for a missing block, a plausible but incorrect replacement, or a defect involving several interacting operations. Keep the scope to the reported execution path.

1. Identify what the caller supplies, what the callee promises, and which observable result is wrong. Gather only the neighboring implementation, an immediate consumer, a relevant surviving test or fixture, and any symmetric operation that can distinguish the alternatives. Treat an example's import or API name as a hypothesis until it matches the checked-out source.

2. Build a short obligation list in reasoning. Record the input condition, required result or exception, the responsible producer, and its downstream consumer. Include the ordinary path as well as the reported edge. Missing, null, false, zero and empty data may have different meanings; derive that distinction from the local API instead of replacing it with a broad truthiness check.

3. Follow the first divergence in the value flow. Look for a removed assignment or validation, a branch that no longer reaches its consumer, an ignored parameter, a missing state update, an altered ordering, or an exit that interrupts required work. A reconstruction should explain why each necessary operation exists. Recover a missing method from its callers and the object's invariants, not by inventing an interface or copying an unrelated function.

4. Select one discriminating probe before a large rewrite. It should distinguish the proposed behavior from the current behavior and from the nearest plausible alternative. Reuse existing objects or fixtures without changing them. Use in-memory assertions with precise observations, including an exception where that is the contract. A normal case that exercises the neighboring branch protects against repairing only the example while breaking ordinary inputs.

5. Preserve the relevant protocol while editing. An iterator must advance, expose the right items and terminate; a parser must consume input and preserve structure; a serializer must retain output shape and ordering; paired conversions must agree on normalization; an accessor or mutator must maintain the object's intended identity and state. Check only the protocol implicated by the source evidence. Do not impose all of these checklists on every task.

6. Once the first correction holds, revisit the unresolved obligations. Inspect one relevant sibling or producer if a remaining symptom points there. Several observations of the same unchanged failure call for a different localization or a better discriminator, not another speculative hunk. A green surviving suite protects established behavior but does not discharge a reported expectation that the suite never exercised.

Finish when the reported obligations, the ordinary path, and the relevant existing regression checks agree with the saved source. Record unavailable execution honestly. Do not read absent hidden tests, alter the harness, write persistent test artifacts, or claim an unexecuted check passed.
