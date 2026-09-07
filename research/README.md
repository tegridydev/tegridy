# Research

Studies in AI, model internals, knowledge systems, numerical methods and security. Each note states the question, the proposed mechanism, what would test it and what remains unresolved. Reference programs demonstrate bounded parts of the methods; they are not trained-model results.

29 articles, grouped by topic. Supporting code and assets stay inside each article folder.

## Agents and assistants

- [Autoresearch: evidence that survives revision](agents/autoresearch-web-researcher/README.md)
- [Local assistant memory: retrieval, validity and reuse](agents/local-assistants-and-memory/README.md)
- [Mixture of Perspectives: preserving useful disagreement](agents/mixture-of-perspectives/README.md)
- [MoA orchestration: routing, events and honest aggregation](agents/moa-framework/README.md)
- [Swarm mechanisms: sequence generation, routing and motion](agents/swarm-and-collective-agent-concepts/README.md)

## Knowledge and linked information

- [CloudVec: measuring index freshness separately from search quality](knowledge/cloudvec-paper-search/README.md)
- [Graph memory with source versions and applicability](knowledge/graph-memory-with-a-paper-trail/README.md)
- [OpenAbstract: correction, evidence and the public reading view](knowledge/open-abstract-knowledge-governance/README.md)
- [SL5: thread-aware evidence and prediction timelines](knowledge/sl5-and-independent-research-workflows/README.md)

## Numerical methods and indexes

- [Four-dimensional summary trees and time-slice queries](mathematics/four-dimensional-lattice/README.md)
- [Hyper Matrix Lattice: adaptive summaries and interval search](mathematics/hyper-matrix-lattice-and-numerical-search/README.md)

## Security and signal research

- [Protocol resource budgets: bytes, work and retained state](security/internet-protocol-amplification-research/README.md)
- [Signal detection under nuisance and session shift](security/sigint-spectrum-analysis-and-covert-channel-concepts/README.md)
- [Security research: evidence, evaluation and open leads](security/tegridydev-security-research-catalogue/README.md)

## Training and evaluation

- [glow-worm: an inspectable byte-language-model baseline](training-and-evaluation/glow-worm-byte-model/README.md)
- [Recursive self-correction: when revision helps and when to stop](training-and-evaluation/recursive-self-correction-with-uncertainty/README.md)
- [Self-rewarding training: objective fidelity and evaluator drift](training-and-evaluation/self-rewarding-training-loops/README.md)

## Transformer mechanisms

- [Arithmetic across notations: testing causal transfer](transformers/arithmetic-across-notations/README.md)
- [BitNet conversion: separate numerical quality from packed execution](transformers/bitnet-quantization-and-conversion/README.md)
- [Face-based attention circuits: a controlled feature-mixing study](transformers/face-based-attention-circuits/README.md)
- [Hydraform: trainable structural adaptation under a fixed budget](transformers/hydraform/README.md)
- [Judge-head attention: measuring contextual influence](transformers/judge-head-attention/README.md)
- [Neuron mapping: selectivity, trajectories and causal checks](transformers/neuron-mapping-and-token-trajectories/README.md)
- [Reflective transformer: causal memory and bounded adaptation](transformers/reflective-transformer-memory-and-adaptation/README.md)
- [Self-healing tokens: recovery without unnecessary edits](transformers/self-healing-tokens/README.md)
- [Sparse feature recovery: reconstruction is only one target](transformers/sparse-feature-recovery/README.md)
- [Adaptive neural architectures: mechanisms and research priorities](transformers/tegridydev-adaptive-neural-architecture-concepts/README.md)
- [Temporal attention: elapsed time inside the prediction](transformers/temporal-attention-that-changes-predictions/README.md)
- [Weight similarity and functional low-rank compression](transformers/weight-similarity-and-svd-compression/README.md)

## Running the included code

Open a module README for its local setup and commands. Python implementations use Python 3.11+, with dependencies listed beside the code. Run tests from the module folder so similarly named standalone examples do not share imports. Browser tools identify their local entry page or loopback address. Saved synthetic results are linked from the relevant article and retain their measurement limits.

[Home](../README.md)

