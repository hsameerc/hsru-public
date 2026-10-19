# HSRU 2.0: Project Preview (Upcoming)

> **"What if an LLM could achieve Transformer-level associative recall and perplexity, but run in microsecond constant time $\mathcal{O}(1)$ with zero KV-cache?"**

We are actively finalizing the release of **HSRU 2.0**, introducing a novel **Predictive Plastic Synaptic Attention** layer paired with neuromorphic recurrence.

---

## The Breakthrough

Transformers suffer from the quadratic $\mathcal{O}(T^2)$ KV-cache crisis, demanding gigabytes of VRAM for long contexts. Meanwhile, existing linear attention and state-space models frequently suffer from **capacity collapse**—their state updates blur overlapping keys, capping associative retrieval.

HSRU 2.0 introduces an error-correcting, factorized memory grid that solves both bottlenecks:
* **Zero KV-Cache:** State size is strictly $\mathcal{O}(1)$ constant. Memory footprint is identical at token 1 and token 1,000,000.
* **No Information Blurring:** Error-erasing updates protect stored facts against destructive interference.
* **Bare-Metal Speed:** Runs on a zero-heap, microsecond C++ engine with zero GPU or external library requirements.

---

## Early Benchmark Teaser

### 1. Multi-Query Associative Recall (SQAR)
*Diagnostic associative key-value retrieval benchmark (15 epochs):*

| Architecture | Parameters | Retrieval Accuracy |
| :--- | :---: | :---: |
| **HSRU 2.0 (Ours)** | **55K** | **100.0%** |
| Standard PyTorch GRU | 29K | 19.5% |
| Causal Multi-Head Transformer (2-Layer) | 103K | 17.8% |
| Standard PyTorch LSTM | 37K | 14.4% |

### 2. Needle-In-A-Haystack Retention
Target facts injected and bombarded with up to **256 random distractor noise tokens** maintained **100.0% retrieval accuracy**, proving zero exponential state decay over long sequences.

### 3. Foundation Language Pretraining (TinyStories)
A 26.3M parameter model trained from scratch on **0.52 Billion tokens** (Chinchilla compute-optimal):
* **Final Validation Loss:** **`1.2317`** (Perplexity: **`3.42`**) — beating 28M GPT-2 (~1.28) and matching 25M Mamba-1 (~1.24).
* **Hardware Footprint:** **1,312 MB VRAM** at Batch 32 $\times$ Seq 1024 ($4\times$ to $5\times$ lower than standard Transformers).
* **Inference Speed:** **10–15 microseconds per token** in C++ on CPU.

#### Unassisted Generation (`Repetition-Penalty = 1.0`, Zero Penalty):
> *"Once upon a time, in a lush green valley, there lived a curious little frog. He hopped around and around the valley, looking for something new. One day, the frog decided to search and see what he could find. He hopped from tree to tree, searching for a place to hide. He hopped around and looked for hours, but nothing seemed to be growing. Finally, he came to a valley, full of colorful flowers. He was so excited that he hopped around the valley, and soon enough, a big, bright red light appeared. The little frog was so excited that he hopped right up and started to jump and play with the bright light. He hopped around and around, until he was too tired to hop anymore and the bright light shone down on him like a giant"*

---

## Full Release Coming Soon

The complete mathematical derivations, formal contractive stability proofs, and full architectural specifications are being prepared and will be unveiled with the official HSRU 2.0 release.

### Private Technical Preview & Research Pilots
We are selectively sharing early foundation checkpoints (`.pt`), raw training logs, and edge-compiled binaries (`.fxp`) with research labs, silicon co-designers (ASIC/FPGA/NPU), and enterprise edge teams.

To request access or discuss research collaboration:
* **Contact:** Sameer Humagain (`im@hsameer.com.np`)
* **Research Updates:** [https://gitlab.com/hsru/hsru-package](https://gitlab.com/hsru/hsru-package)
* **Public Release Hub:** [https://github.com/hsameerc/hsru-public](https://github.com/hsameerc/hsru-public)
