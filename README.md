# [td] tegridydev

**personal blog, research, writing and ideas**

This is where I keep the things I've written up and made ready to share. All my stuff is open knowledge, so feel free to read through and use it however you see fit <3

Mostly AI, security, tooling + ideas & things I've been building.

I also use this space to work through research questions, explore weird ideas and occasionally wander off into abstract tangents :)

[Blog](#blog) · [Research](#research) · [Running the code](#running-the-code)

## Blog

Practical tools, experiments and the questions behind them. [Open the blog index](blog/README.md).

### Agents and assistants

- [botsim: letting the locals talk](blog/agents/botsim-local-community/README.md)
- [minecraft time with astra](blog/agents/minecraft-time-with-astra/README.md)

### Applications and utilities

- [getting a useful export out of a chat log](blog/applications/discord-log-export-and-field-extraction-toolkit/README.md)
- [image conversion has more edge cases than the button suggests](blog/applications/image-conversion-resizing-and-privacy/README.md)
- [pulling useful fields out of messy text](blog/applications/lead-extraction-and-cleaning/README.md)

### Datasets and document tools

- [cleaning a dataset without cleaning away its meaning](blog/datasets/dataset-discovery-and-preparation/README.md)
- [collecting papers without losing why I wanted them](blog/datasets/paper-and-book-collection/README.md)
- [a readable PDF export can still be wrong](blog/datasets/pdf-extraction-and-markdown/README.md)
- [making synthetic data I can actually check](blog/datasets/synthetic-data-generation-and-quality/README.md)

### Developer workflows

- [doing research without losing the question](blog/developer-tools/research-without-losing-the-question/README.md)

### Knowledge and linked information

- [an embedding column needs more than a convincing name](blog/knowledge/embeddings-need-a-contract/README.md)
- [knowledge bases should help me choose the next check](blog/knowledge/knowledge-bases-that-help-with-real-work/README.md)
- [sorting old notes without rewriting history](blog/knowledge/sorting-notes-without-rewriting-history/README.md)
- [xanadu-2: links that remember what they point to](blog/knowledge/xanadu-linked-documents/README.md)

### Model interpretability

- [what am I actually looking at in a model map?](blog/model-interpretability/what-a-model-map-can-show/README.md)

## Research

Model mechanisms, agent systems, knowledge tools, numerical methods and security studies. Articles distinguish proposed experiments, tested components and observed pilot results. [Open the research index](research/README.md).

### Agents and assistants

- [Autoresearch: evidence that survives revision](research/agents/autoresearch-web-researcher/README.md)
- [Local assistant memory: retrieval, validity and reuse](research/agents/local-assistants-and-memory/README.md)
- [Mixture of Perspectives: preserving useful disagreement](research/agents/mixture-of-perspectives/README.md)
- [MoA orchestration: routing, events and honest aggregation](research/agents/moa-framework/README.md)
- [Swarm mechanisms: sequence generation, routing and motion](research/agents/swarm-and-collective-agent-concepts/README.md)

### Knowledge and linked information

- [CloudVec: measuring index freshness separately from search quality](research/knowledge/cloudvec-paper-search/README.md)
- [Graph memory with source versions and applicability](research/knowledge/graph-memory-with-a-paper-trail/README.md)
- [OpenAbstract: correction, evidence and the public reading view](research/knowledge/open-abstract-knowledge-governance/README.md)
- [SL5: thread-aware evidence and prediction timelines](research/knowledge/sl5-and-independent-research-workflows/README.md)

### Numerical methods and indexes

- [Four-dimensional summary trees and time-slice queries](research/mathematics/four-dimensional-lattice/README.md)
- [Hyper Matrix Lattice: adaptive summaries and interval search](research/mathematics/hyper-matrix-lattice-and-numerical-search/README.md)

### Security and signal research

- [Protocol resource budgets: bytes, work and retained state](research/security/internet-protocol-amplification-research/README.md)
- [Signal detection under nuisance and session shift](research/security/sigint-spectrum-analysis-and-covert-channel-concepts/README.md)
- [Security research: evidence, evaluation and open leads](research/security/tegridydev-security-research-catalogue/README.md)

### Training and evaluation

- [glow-worm: an inspectable byte-language-model baseline](research/training-and-evaluation/glow-worm-byte-model/README.md)
- [Recursive self-correction: when revision helps and when to stop](research/training-and-evaluation/recursive-self-correction-with-uncertainty/README.md)
- [Self-rewarding training: objective fidelity and evaluator drift](research/training-and-evaluation/self-rewarding-training-loops/README.md)

### Transformer mechanisms

- [Arithmetic across notations: testing causal transfer](research/transformers/arithmetic-across-notations/README.md)
- [BitNet conversion: separate numerical quality from packed execution](research/transformers/bitnet-quantization-and-conversion/README.md)
- [Face-based attention circuits: a controlled feature-mixing study](research/transformers/face-based-attention-circuits/README.md)
- [Hydraform: trainable structural adaptation under a fixed budget](research/transformers/hydraform/README.md)
- [Judge-head attention: measuring contextual influence](research/transformers/judge-head-attention/README.md)
- [Neuron mapping: selectivity, trajectories and causal checks](research/transformers/neuron-mapping-and-token-trajectories/README.md)
- [Reflective transformer: causal memory and bounded adaptation](research/transformers/reflective-transformer-memory-and-adaptation/README.md)
- [Self-healing tokens: recovery without unnecessary edits](research/transformers/self-healing-tokens/README.md)
- [Sparse feature recovery: reconstruction is only one target](research/transformers/sparse-feature-recovery/README.md)
- [Adaptive neural architectures: mechanisms and research priorities](research/transformers/tegridydev-adaptive-neural-architecture-concepts/README.md)
- [Temporal attention: elapsed time inside the prediction](research/transformers/temporal-attention-that-changes-predictions/README.md)
- [Weight similarity and functional low-rank compression](research/transformers/weight-similarity-and-svd-compression/README.md)

## Running the code


Supporting implementations accompany the articles. Each project README lists its entry points, dependencies and commands. The [reproduction guide](tools/studies/README.md) uses uv and pinned Python 3.12 dependencies to run the studies and their checks; browser tools identify their HTML entry point.

Forty entries include recorded workflow checks or CPU comparisons, covering 140 runs. The articles distinguish functional checks, comparative experiments and proposals, and retain negative and inconclusive findings. Original pilot records remain available alongside the larger comparisons.

[Back to top](#td-tegridydev)

[Website](https://tegridydev.com/) · [GitHub](https://github.com/tegridydev) · [Hugging Face](https://huggingface.co/tegridydev)
