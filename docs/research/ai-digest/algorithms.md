# Algorithms: SMC and Related Methods

## Locally Constrained Decoding

- Applies constraints at each token step (e.g., logit masking).
- Efficient for simple constraints, but can be greedy and myopic.

## Importance Sampling (IS)

- Samples from a proposal (e.g., locally constrained decoding), then reweights samples to correct for proposal bias and add expensive potentials.
- Weight: w(i) = [p(x(i))Φ(x(i))] / ℓeff(x(i))

## Sequential Monte Carlo (SMC)

- Generalizes IS by incrementally extending, reweighting, and resampling particles (partial sequences).
- Steps:
  1. Extend: Sample next token for each particle.
  2. Reweight: Update weights using efficient and expensive potentials.
  3. Resample: Focus computation on promising particles.
- Allows incremental use of constraints and adapts computation.

## Set-Based Proposal Speedup

- For expensive constraints, samples a subset of tokens/characters and uses Horvitz–Thompson estimator for unbiased weighting.
- Trie-based character-level proposals for grammar constraints.

See implementation.md for code linkage and domains.md for applications.
