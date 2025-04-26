# Key Concepts

## Controlled Generation

- Generating text from LLMs under syntactic/semantic constraints.
- Constraints can be hard (e.g., grammar, type-checking) or soft (e.g., reward models).

## Potential Functions

- Potentials ϕ(x): non-negative scores for token sequences x.
- Set of potentials Φ(x) = ∏ϕ∈Φ ϕ(x).

## Product of Experts Distribution

- Target: g(x) ∝ p(x)Φ(x), where p(x) is the LM base distribution.
- Sampling from g(x) is generally intractable for non-trivial Φ.

## Constraint Types

- Φeff: Efficient, can be checked incrementally (e.g., grammar, prefix validity).
- Φexp: Expensive, checked less frequently (e.g., test execution, simulation).

## Domains

- Python code generation (DS-1000)
- Text-to-SQL (Spider)
- Goal inference (PDDL/STRIPS)
- Molecular synthesis (SMILES)

See algorithms.md for inference methods and implementation.md for code linkage.
