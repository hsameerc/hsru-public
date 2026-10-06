<div align="center">
  <h1>🚀 HSRU: Hybrid State Recurrent Unit</h1>
  <h3>The Post-Transformer Foundation Architecture for Edge AI</h3>
  
  [![License](https://img.shields.io/badge/License-MIT-blue.svg)](#)
  [![C++ Edge](https://img.shields.io/badge/Engine-C%2B%2B%20%7C%20Zero%20Deps-orange)](#)
  [![Looking for Investors](https://img.shields.io/badge/Status-Seeking%20Seed%20Funding-success)](#)
  [![Collab](https://img.shields.io/badge/Collaboration-Open-purple)](#)
</div>

---

Welcome to the **HSRU Release SDK**. 

I am a solo researcher who has built a novel, mathematically stable $\mathcal{O}(1)$ neural architecture designed to match the associative recall capabilities of Transformers **without the prohibitive memory scaling of the KV-Cache**. 

HSRU is a true multi-modal foundation architecture built to natively process language, continuous audio waveforms, and drone/robotics telemetry using a unified Spiking Memory engine.

## 🤝 Call for Collaboration & Investment
**I am currently building this alone and am actively seeking financial support, venture capital, deep-tech grants (NSF/DARPA), and technical collaborators to help scale HSRU to the 1B+ parameter regime and commercialize this technology.**

If you are an investor, grant officer, or a passionate engineer who sees the potential of replacing Transformers on edge devices, let's talk!

---

### 1. Key Architectural Innovations
Transformers rely on unbounded attention matrices, making them mathematically uncertifiable for safety-critical edge environments. HSRU replaces this with:

*   **Spiking Linear Attention (PKM):** HSRU utilizes a discrete spiking mechanism to perform sparse Top-K memory routing. This allows the model to retrieve exact memories in linear time ($\mathcal{O}(1)$ memory footprint) without calculating dense attention scores.
*   **Convex Blending for Safety (DO-178C):** In aerospace and robotics, software must guarantee Bounded-Input Bounded-Output (BIBO) stability. The HSRU `blend` mode strictly bounds state updates using convex combinations ($\beta \in [0, 1]$), ensuring the model cannot mathematically diverge.
*   **Hardware-Friendly Approximations:** The internal logic gates utilize piecewise linear approximations ($\sigma_{hw}$) instead of transcendental functions, maximizing inference speed on constrained microcontrollers.

---

### 2. Edge C++ SDK Demonstrations
To prove the architecture's efficiency, I have built fully self-contained C++ executables. These demos run the pre-trained integer-quantized (`--fxp`) weights natively on your CPU. 

**Zero dependencies required. No Python, no PyTorch, no GPU.**

#### 🚁 A. HSRU-Drone (Predictive Maintenance & Anomaly Detection)
A real-time edge anomaly detector running on raw drone IMU telemetry. Instead of classification, it uses predictive physics modeling to instantly detect mechanical failures (like a broken propeller) the millisecond they happen.
*   **Math Parity:** 100% Verified against PyTorch
*   **Detection Rate:** 100% on UAV Propeller Fault Dataset
*   **Safety Features:** Dynamic Six Sigma Auto-Calibration & TBPTT

#### 💬 B. HSRU-Small (Text Generation)
A 26M parameter language model trained on the TinyStories corpus to prove discrete logic capabilities.
*   **Inference Speed:** ~126 tokens/sec (Tested on Apple Silicon)
*   **Memory Profile:** $\mathcal{O}(1)$ Constant Memory
*   **How to run (macOS):**
    ```bash
    cd Demos/Mac_HSRU_Small
    ./hsru_edge
    ```

#### 🎵 C. HSRU-Encodec (Audio Compression)
An 82.6M parameter continuous audio codec proving the architecture's ability to compress and reconstruct high-dimensional continuous waveforms.
*   **L1 Waveform Error:** 0.045
*   **Processing Speed:** 6.5x Real-Time Factor (RTF) on Apple Silicon CPU
*   **How to run (macOS):**
    ```bash
    cd Demos/Mac_HSRU_Encodec
    ./inference test.wav out.wav
    ```

---

### 3. Included Whitepapers
Inside the `Whitepapers/` directory, you will find the mathematical proofs for the architecture:
- **`hsru_mathematics.pdf`**: The core architectural derivations, detailing the transition from continuous state spaces to discrete Spiking memory.
- **`hsru_verification.pdf`**: Detailed analysis on safety verification, convex blending stability bounds, and DO-178C compliance for edge robotics.

---

### 🚀 Join the Mission
The PyTorch training infrastructure, highly-optimized CUDA kernels, distributed data pipelines, and multi-node training scripts are currently proprietary. I am looking for the right partners to open-source, commercialize, or scale this. 

**Let's build the post-Transformer era of Edge AI together.**
