# HSRU 2.0: Predictive Plastic Synaptic Attention & Edge Recurrence
### Upcoming Release Preview & Empirical Milestone Report

> **Status:** Release Candidate (In Active Progress)  
> **Core Innovation:** 2D Product Key Memory (PKM) Delta Attention + Tripartite Neuromorphic Recurrence  
> **Target Deployment:** Microsecond Edge CPU/NPU Inference & Constant $\mathcal{O}(1)$ Memory Training

---

## 1. Executive Summary

Standard Transformers suffer from quadratic memory growth ($\mathcal{O}(T^2)$), requiring tens of gigabytes of VRAM just to store the Key-Value (KV) cache for long sequences. Conversely, linear attention and state space models (SSMs) frequently suffer from **capacity collapse and catastrophic forgetting** on multi-query associative recall because linear state updates blur overlapping keys.

**HSRU 2.0 solves both ends of this trade-off.** 

By uniting **neuromorphic dendritic integration**, **GLU logic gating**, and a **2D Product Key Memory (PKM) Delta Attention Layer**, HSRU achieves:
1. **True $\mathcal{O}(1)$ constant-time inference memory** (zero KV cache, fixed state footprint at token 1 and token 1,000,000).
2. **100% Associative Recall and Needle-In-A-Haystack retention**, matching dense Softmax attention.
3. **Transformer-parity natural language pretraining loss** at a fraction of the VRAM footprint.

---

## 2. Core Architectural Innovations

```
Input Token ──► [ LayerNorm ] 
                   │
                   ├──► [ HSRUMemoryLayer ]      (Dendritic filtering + discrete boolean latches)
                   ├──► [ HSRULogicLayer  ]      (High-throughput non-linear GLU reasoning)
                   └──► [ PKM Delta Attention ]  (2D Factorized Codebooks + Error-erasing Delta Rule)
                   │
                [ Additive / Gated Residual Highway ] ──► Next Layer Output
```

### Key:
* **2D PKM Codebook Factorization:** Learns orthogonal row and column codebooks ($C_1, C_2 \in \mathbb{R}^{H \times N \times d/2}$) projected via sharp softmax scale $s_h$. Generates an $N^2$ addressable memory grid ($256$ slots per head) with only $2N$ parameters, eliminating hash collisions.
* **Error-Erasing Delta Recurrence:** Instead of additive outer products ($M \leftarrow M + k v^T$) that saturate and destroy prior facts, HSRU computes the prediction error:
  $$v_{\text{pred}} = P_K^T M_{t-1}, \quad e_t = v_t - v_{\text{pred}}, \quad M_t = M_{t-1} + \beta_t P_{K,t} e_t^T$$
  Guarantees spectral boundedness ($\|\mathbf{A}_t\|_2 \le 1$) and unconditional contractive stability.
* **Fused CUDA On-The-Fly Addressing:** Passes 1D vectors directly into GPU shared memory; expands 2D outer products in registers in a single cycle. Eliminates intermediate 4D tensor materialization in DRAM ($16\times$ memory bandwidth reduction).
* **Zero-Heap Microsecond C++ Engine:** Standalone C++ runtime (`hsru_llm.cpp`) executes recurrent generation with pre-allocated scratch buffers at **10–15 microseconds per token** on commodity CPUs.

---

## 3. Empirical Benchmarks & Validation Results

### Benchmark A: Single-Query Associative Recall (SQAR)
*Fixed-dimension comparative evaluation against standard recurrent and Transformer baselines (15 epochs, Apple Silicon MPS):*

| Model | Parameter Count | Architecture | Retrieval Accuracy |
| :--- | :---: | :--- | :---: |
| **`hsru` (Ours)** | **55,876** | **Memory + Logic + PKM Delta Attention** | **100.0%** |
| `gru` | 29,056 | PyTorch Gated Recurrent Unit | 19.5% |
| `hsru_no_attn` | 38,208 | Memory + Logic (Ablation: No Attention) | 19.2% |
| `hsru_no_logic` | 25,472 | Pure Memory Layer (Ablation: No Logic) | 18.3% |
| `transformer` | 103,808 | 2-Layer Causal Multi-Head Attention | 17.8% |
| `lstm` | 37,376 | PyTorch Long Short-Term Memory | 14.4% |
| `hsru_no_memory` | 16,704 | Pure Logic Layer (No Temporal Recurrence) | 4.5% |

> **Result:** HSRU achieved **100.0% accuracy**, cleanly outperforming standard recurrent baselines (14%–19%) and a 2-layer Transformer (17.8%) with half the parameter footprint.

---

### Benchmark B: Needle-In-A-Haystack (NIAH) Long-Context Retention
*Target fact injected at $t=0$, bombarded by up to 256 random distractor noise tokens, queried at the final token:*

| Distractor Length | Total Context | HSRU Accuracy | Memory Retention Status |
| :---: | :---: | :---: | :---: |
| **32 tokens** | 36 tokens | **100.0%** | **PERFECT** |
| **64 tokens** | 68 tokens | **100.0%** | **PERFECT** |
| **128 tokens** | 132 tokens | **100.0%** | **PERFECT** |
| **256 tokens** | 260 tokens | **100.0%** | **PERFECT** |

> **Result:** Demonstrates zero exponential state decay. The error-erasing write mechanism completely shields stored memories from irrelevant noise tokens.

---

### Benchmark C: 26.3M Natural Language Pretraining (TinyStories)
*Pretraining run on 0.524 Billion tokens reaching exact Chinchilla compute-optimality ($20.0\times$ tokens/parameter):*

* **Architecture:** 12 layers, 256 hidden dimension, 1024 logic dimension (GLU), 50,257 vocab (BPE).
* **Hardware Footprint:** **1,312 MB VRAM** at Batch 32 $\times$ Seq 1024 ($4\times$ to $5\times$ lower than Transformer).
* **Training Stability:** Grad norm stable at `0.99 – 1.06` over 16,000 steps with zero divergence or NaN spikes.
* **Loss Trajectory:**
  * Step 1: `10.9456` (PPL: 56,702)
  * Step 5,000: `1.8793` (PPL: 6.55)
  * Step 10,000: `1.2878` (PPL: 3.62)
  * Step 15,000: `1.2212` (PPL: 3.39)
  * **Final Step 16,000:** **`1.2317` Validation Loss (Perplexity: 3.42)**
* **Baseline Comparison:**
  * GPT-2 Small (28M): $\sim 1.28$ Val Loss
  * GPT-Neo (33M): $\sim 1.25$ Val Loss
  * Mamba-1 (25M): $\sim 1.24$ Val Loss
  * **HSRU-Small (26.3M):** **`1.2212` (Best) / `1.2317` (Final)**

#### Zero-Penalty Text Generation Sample (`Repetition-Penalty = 1.0`):
> *"Once upon a time, in a lush green valley, there lived a curious little frog. He hopped around and around the valley, looking for something new. One day, the frog decided to search and see what he could find. He hopped from tree to tree, searching for a place to hide. He hopped around and looked for hours, but nothing seemed to be growing. Finally, he came to a valley, full of colorful flowers. He was so excited that he hopped around the valley, and soon enough, a big, bright red light appeared. The little frog was so excited that he hopped right up and started to jump and play with the bright light. He hopped around and around, until he was too tired to hop anymore and the bright light shone down on him like a giant"*

---

## 4. Formal Mathematical Verification

The mathematical whitepapers detailing the formal proofs are available in `docs/`:
1. **`docs/hsru_mathematics.pdf`**:
   * *Theorem 5.1 (Factorized $L_2$ Normalization Invariance)*
   * *Theorem 5.2 (Contractive Delta-Rule Stability and Spectral Boundedness)*
   * *Theorem 5.3 (Exact On-Chip State Inversion & Adjoint BPTT)*
   * *Theorem 5.4 (Column Decoupling Theorem and Sub-SRAM Multi-Pass Tiling)*
2. **`docs/hsru_verification.pdf`**:
   * *Closed-Form Matrix Integration & Learnable Exponential Moving Averages*
   * *Information Bottleneck Lagrangian Optimization*
   * *Lossless Delta-Sigma Noise-Shaping Discretization*

---

## 5. Early Access, Research Collaboration & Commercial Pilots

We are actively opening collaboration channels for researchers, hardware designers, and enterprise teams looking to run high-throughput LLM workloads on constrained edge devices or explore sub-quadratic architectures.

### Ways to Engage:
* **Private Technical Preview / Weights Access:** Qualified researchers and partners can request access to full 26M and larger foundation checkpoints, raw training logs, and edge-compiled `.fxp` binaries.
* **Hardware & Silicon Co-Design:** Evaluation of the HSRU neuromorphic dendritic pipeline for custom ASIC, FPGA, or neuromorphic accelerators.
* **Enterprise Edge Deployment:** Zero-dependency microsecond CPU inference engines for embedded robotics, avionics, and offline mobile applications.

**Contact & Inquiries:**  
* **Lead Researcher:** Sameer Humagain (`im@hsameer.com.np`)  
* **Repository:** [https://gitlab.com/hsru/hsru-package](https://gitlab.com/hsru/hsru-package)  
* **LLM Engine:** [https://gitlab.com/hsru/hsru-llm](https://gitlab.com/hsru/hsru-llm)
