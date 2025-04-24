# Implementation Notes and Code Linkage

## Grammar-Based Potentials

- Use efficient prefix-checking algorithms (Earley, Stolcke, etc.) for Φeff.
- Character-level proposals can use trie structures for grammar enforcement.

## SMC/IS Algorithms

- Place core SMC/IS logic in modules related to inference/sampling (e.g., /context_engine/tools/ or /mcp_context_engine/tools/).
- Modularize domain-specific potentials for easy extension (e.g., test case execution, molecule validation).

## Resampling

- Use multinomial resampling with effective sample size threshold.

## Linking to Code

- Tag code files implementing SMC, IS, and constraint logic with #sequential-monte-carlo, #importance-sampling, #grammar-constraints, etc.
- Reference this digest in code documentation for maintainability.

See tags.md for tag definitions and references.md for further reading.
