# ⚡ HSRU 2.0 — Official Teaser

> *"What if an LLM could achieve high-fidelity associative recall and language modeling, while running with constant $\mathcal{O}(1)$ memory and constant per-token cost, with zero KV-cache?"*

---

### 🚨 Something New Is Coming.
**Official Unveiling Coming Soon.**

We are finalizing the public launch of **HSRU 2.0**, introducing a novel **Predictive Plastic Synaptic Attention** architecture paired with neuromorphic recurrence.

---

## 🔮 The Core Mystery: Can Recurrence Truly Scale?

Standard Transformers carry an ever-expanding Key-Value (KV) cache that inflates memory with every generated token, choking edge devices. Meanwhile, traditional recurrent architectures suffer from memory interference and catastrophic forgetting—blurring facts together as context grows.

**HSRU 2.0 rewrites this paradigm with an error-correcting, factorized memory grid:**

* ⚡ **Zero KV-Cache ($\mathcal{O}(1)$ Memory):** Memory footprint is strictly constant. It consumes the exact same memory at token 1 as it does at token 1,000,000.
* 🧠 **Non-Destructive Recurrence:** Novel error-erasing synaptic updates continuously guard stored facts against memory interference.
* 🏎️ **Bare-Metal CPU Inference:** Standalone, zero-heap C++ engine requiring zero GPU, zero CUDA, and zero external dependencies for inference. Per-token cost stays constant regardless of context length.

---

## 📊 Sneak Peek: Raw Empirical Benchmarks

*No cherry-picking. No theoretical hand-waving. Here is a glimpse of what the engine does:*

### 🎯 1. Associative Memory & Needle Retrieval
* **Single-Query Associative Recall (SQAR):** Reached **100.0% retrieval accuracy** in diagnostic key-value recall within 15 epochs.
* **Needle-In-A-Haystack Retention:** Injected target facts bombarded with up to **256 random distractor noise tokens** maintained **100.0% retrieval accuracy**, with no measurable decay at that distance (longer-range and multi-query tests are in progress).

### 📈 2. Foundation Pretraining (26.3M Parameters)
Trained from scratch on **0.52 Billion tokens** across 16,000 steps on consumer hardware:
* **Validation Loss:** **`1.2317`** (Perplexity: **`3.42`**)
* **Hardware Footprint:** **1,312 MB VRAM** at Batch 32 $\times$ Context 1024
* **Inference Throughput:** **~116–135 tokens/sec** (~7–9 ms per token) on an Apple Silicon CPU, constant across context length

#### Raw Story Generation Sample (`rep_penalty = 1.0` — Zero Repetition Penalty):
> *"Once upon a time, in a lush green valley, there lived a curious little frog. He hopped around and around the valley, looking for something new. One day, the frog decided to search and see what he could find. He hopped from tree to tree, searching for a place to hide. He hopped around and looked for hours, but nothing seemed to be growing. Finally, he came to a valley, full of colorful flowers. He was so excited that he hopped around the valley, and soon enough, a big, bright red light appeared. The little frog was so excited that he hopped right up and started to jump and play with the bright light. He hopped around and around, until he was too tired to hop anymore and the bright light shone down on him like a giant"*

---

## 📜 Full Release Coming Soon

The complete mathematical whitepapers, formal contractive stability proofs, and full architectural specifications **will be unveiled alongside the official HSRU 2.0 release**.

### 🔒 Exclusive Research Pilots & Early Previews
Prior to the public launch, early foundation checkpoints (`.pt`), raw training logs, and edge-compiled binaries (`.fxp`) are being made available selectively to:
- Academic research labs & LLM architecture researchers
- Silicon co-design teams (ASIC / FPGA / NPU acceleration)
- Edge AI & real-time embedded engineering groups

**To request exclusive preview access:**
* ✉️ **Contact:** Sameer Humagain ([im@hsameer.com.np](mailto:im@hsameer.com.np?subject=HSRU%202.0%20Exclusive%20Preview))
* 🌐 **Public Release Hub:** [https://github.com/hsameerc/hsru-public](https://github.com/hsameerc/hsru-public)
* 🔬 **Research Updates:** [https://gitlab.com/hsru/hsru-package](https://gitlab.com/hsru/hsru-package)
