<div align="center">
  <h1>⚡ HSRU: Hybrid State Recurrent Unit</h1>
  <h3>A post-Transformer multi-modal foundation architecture for edge AI</h3>
  
  [![C++ Edge Engine](https://img.shields.io/badge/Runtime-C%2B%2B%20%7C%20GGML%20%7C%20Zero--Deps-orange.svg)](#-edge-c-sdk-demonstrations-black-box-evaluation)
  [![Memory Footprint](https://img.shields.io/badge/Memory-%F0%9F%AA%84%20O(1)%20Constant%20Footprint-blue.svg)](#-architecture-overview)
  [![Mathematics](https://img.shields.io/badge/Mathematics-Fully%20Open-brightgreen.svg)](#-repository-scope-what-is-public-vs-proprietary)
  [![Source Code](https://img.shields.io/badge/Source-Proprietary%20%7C%20Open%20for%20Collaboration-purple.svg)](#-repository-scope-what-is-public-vs-proprietary)
  [![Status](https://img.shields.io/badge/Status-Open%20for%20Collaboration-success.svg)](#-open-collaboration-taking-hsru-further)
</div>

---

## 💡 The Core Thesis

Transformers work well in cloud data centers, but they run into real thermodynamic and memory bottlenecks on edge hardware: **quadratic $O(T^2)$ computational complexity and the fast-growing Key-Value (KV) cache**. 

To generate tokens or stream audio, standard self-attention must retain preceding timesteps in active RAM. On an embedded drone, wearable, phone, or microcontroller, the KV cache quickly consumes available memory, leading to thermal throttling, latency spikes, and battery drain.

**HSRU (Hybrid State Recurrent Unit)** is an alternative recurrent architecture built to remove this bottleneck. By combining **biological leaky integrate-and-fire dynamics**, **discrete threshold gates**, and **continuous non-linear logic pathways**, HSRU delivers:

1. **$\mathcal{O}(1)$ Constant Memory:** RAM usage stays flat whether the sequence runs for 10 seconds or 10 hours.
2. **Linear $\mathcal{O}(T)$ Time:** Deterministic, flat latency per token or telemetry frame.
3. **Multi-Modal Processing:** A single shared mathematical core handles **Language Tokens**, **Continuous Audio Waveforms**, and **High-Frequency Drone IMU Telemetry**.

---

## 📦 Repository Scope: What is Public vs. Proprietary

To ensure full transparency for researchers, engineers, and collaborators, here is how this repository is structured:

| Component | Status | Location & Details |
|---|:---:|---|
| **Mathematical Whitepapers & Proofs** | **Fully Open** | [Whitepapers/](Whitepapers/) (Complete derivations for BIBO stability, convex blending, and bounded Jacobians) |
| **Pre-Compiled Black-Box Demos** | **Public Evaluation Binaries** | [Demos/](Demos/) (Standalone native C++ binaries across macOS, Linux, and Windows for zero-setup testing) |
| **Benchmark Logs & Metrics** | **Fully Open** | [DRONE_METRICS.md](DRONE_METRICS.md), [TRAINING_METRICS.md](TRAINING_METRICS.md), and [Metrics/](Metrics/) |
| **Model Weights & GGUF Payloads** | **Public Evaluation Use** | Pre-trained weights included inside [Demos/](Demos/) for direct execution |
| **Core Training Framework (PyTorch)** | **Proprietary** | Private repository; available for research partnerships and pilot collaborations |
| **Custom Fused CUDA Kernels** | **Proprietary** | Private repository; available for compute scaling and acceleration partnerships |
| **C++ Inference Engine Source Code** | **Proprietary** | Private repository; available under collaboration or licensing agreements |

### Why Open Mathematics with Black-Box Demos?

* **Open Scientific Verification:** The theoretical foundations, equations, and mathematical safety guarantees are completely open in the whitepapers. You can independently review the math, verify the stability bounds, and audit the derivations without restrictions.
* **Immediate Zero-Friction Testing:** The standalone binaries in [Demos/](Demos/) operate as self-contained black-box builds. You can test inference throughput, verify sub-millisecond reaction latency, and inspect the flat $\mathcal{O}(1)$ RAM footprint on your local machine without configuring Python virtual environments, PyTorch versions, or CUDA drivers.
* **Proprietary Implementation & Open Collaboration:** The underlying source code (training framework, custom CUDA kernels, and native C++ runtime) is the author's proprietary technology developed from first principles. It is not open-source for public redistribution, but full source code access and developer tooling are actively shared for joint research collaborations, hardware integrations, and commercial licensing.

---

## 🤝 Open Collaboration: Taking HSRU Further

> "I built HSRU from first principles, taking it from raw equations on paper all the way to working, zero-dependency C++ runtimes and benchmarked models across Language, Continuous Audio, and UAV Telemetry. If you find this work interesting and want to explore, experiment, or take it even further together, feel free to reach out anytime. No formality, no hesitation."

### 🗺️ The Roadmap
* ✅ **Phase 1: Foundations and Verification (Complete):** Validated mathematical stability, bounded Jacobians, and expressive parity across Text, Audio, and Telemetry in the 26M to 83M parameter range.
* ✅ **Phase 2: Standalone Edge SDK (Complete):** Built native C++ and **GGML/GGUF** runtimes, completely decoupling high-speed inference from Python, PyTorch, or CUDA with bounded $\mathcal{O}(1)$ RAM.
* 🚀 **Phase 3: Multi-Modal Scaling and Real-World Deployments (Current Focus):**
    * **Autonomous Drones and Avionics:** Hardware-in-the-loop flight controller integration (Pixhawk / PX4 / ArduPilot) for live, sub-millisecond structural health monitoring and zero-false-alarm propeller fault detection.
    * **Continuous Neural Audio:** High-efficiency, ultra-low-latency neural speech and music codecs running on embedded DSPs and consumer wearables.
    * **Language and Foundation Models:** Scaling parameter count and context length with flat linear memory, removing the KV-cache bottleneck.
    * **Biomedical Telemetry (ECG / Cardiac Health):** Applying continuous $\mathcal{O}(1)$ spiking recurrence to 24/7 wearable cardiac telemetry for instantaneous arrhythmia and anomaly detection without battery drain.

Whether you are a robotics engineer, audio researcher, medical tech developer, or someone interested in alternative edge architectures, my inbox is open. Let's connect, share ideas, and build.

### 📬 Direct Contact
| | |
|---|---|
| **Author** | **Sameer Humagain** |
| **Email** | [im@hsameer.com.np](mailto:im@hsameer.com.np?subject=HSRU%20Collaboration) |
| **GitHub** | [@hsameerc](https://github.com/hsameerc) |

---

## 🧠 Architecture Overview

Standard RNNs often struggle with vanishing gradients and poor recall, while Transformers solve recall at the cost of high memory usage. HSRU addresses both by combining three core mechanisms:

```text
Input Feature Vector x[t]
          │
    ┌─────┴──────────────────────────────────────────────────────┐
    │  Fused Linear Projections (Leak, Shunt, Soma, Dendrites)   │
    └─────┬──────────────────────────────────────────────────────┘
          │
    ┌─────▼──────────────────────────────────────────────────────┐
    │  Spatiotemporal Dendritic Integration (Event Detection)    │
    └─────┬──────────────────────────────────────────────────────┘
          │
    ┌─────▼──────────────────────────────────────────────────────┐
    │  Split-Brain Recurrent Memory Layer                        │
    │  ├─ Channels 0..dim/2: Spiking Mode (Thermometer k-dims)   │
    │  └─ Channels dim/2..dim: Continuous Leaky Mode (Sigmoid)   │
    └─────┬──────────────────────────────────────────────────────┘
          │
    ┌─────▼──────────────────────────────────────────────────────┐
    │  GLU Logic Layer + Sinusoidal Positional Clock Dynamics    │
    └─────┬──────────────────────────────────────────────────────┘
          │
Reconstructed Output Vector h[t]
```

### Key Technical Pillars:
* **Spiking Thresholds ($k\_dims$):** Channels $0$ to $\frac{\text{dim}}{2}$ use discrete voltage thresholds to create sparse, event-driven firing. This provides selective memory routing without dense attention matrices.
* **Continuous Semantic Channels:** Channels $\frac{\text{dim}}{2}$ to $\text{dim}$ integrate continuous floating-point state for smooth contextual reasoning.
* **Snake Periodic Activations:** Custom periodic activation functions ($\text{Snake1d}$) preserve periodic phase dynamics and high-frequency harmonics without phase distortion.
* **Topological Graph Allocation (`ggml_gallocr`):** Memory buffers are dynamically recycled across computation steps, keeping runtime RAM footprints below **270 MB**.

---

## 🛡️ Safety and Stability Guarantees

In avionics, robotics, and medical devices, model behavior must remain bounded. Unconstrained attention mechanisms can behave unpredictably on out-of-distribution inputs.

* **BIBO Stability (Bounded-Input Bounded-Output):** The HSRU `blend` mode strictly constrains recurrent state updates using convex combinations ($\beta \in [0, 1]$), ensuring internal states cannot numerically diverge.
* **DO-178C Alignment:** Core mathematical operations use hardware-bounded approximations ($\sigma_{hw}$) with no unbounded transcendental loops, ensuring deterministic execution time.
* **Full Derivations:** Mathematical proofs and derivations are available in [Whitepapers/hsru_mathematics.pdf](Whitepapers/hsru_mathematics.pdf) and [Whitepapers/hsru_verification.pdf](Whitepapers/hsru_verification.pdf).

---

## 💻 Edge C++ SDK Demonstrations (Black-Box Evaluation)

To test the architecture easily without needing source builds, this repository includes pre-compiled, standalone black-box C++ binaries. **No Python, PyTorch, or CUDA installation is required.**

| Demo Module | Modality | macOS (Apple Silicon) | Linux (x86_64) | Windows (x64) | Engine |
|---|---|:---:|:---:|:---:|:---:|
| **HSRU-Encodec** | 24 kHz Neural Audio | ✅ Current | 🔄 In SDK | 🔄 In SDK | **GGML + GGUF v3** |
| **HSRU-Small** | 26M Autoregressive Text | ✅ Current | ✅ Current | ✅ Current | **Native C++ v1** |
| **HSRU-Drone** | UAV Propeller Anomaly Detection | - | ✅ Current | - | **Native C++ v1** |

---

### 🎵 1. HSRU-Encodec (Continuous Neural Audio Compression)
An 82.6M parameter end-to-end neural audio codec demonstrating HSRU's ability to compress and reconstruct continuous 24,000 Hz waveforms.

* **Performance:** **>4.1x faster than real-time** on Apple Silicon CPU (RTF: $0.24\times$).
* **Fidelity:** **>96.9% numerical correlation** with PyTorch reference, **8.8+ dB SNR**.
* **Memory Buffer:** **<270 MB** compute memory via topological graph allocator.
* **Quantization:** INT8 / FP16 GGUF payload (97 MB, direct Git tracking without Git LFS).
* **Audio Ingestion:** Supports standard `.wav` files (mono or stereo, 16/24/32-bit); downmixes to mono and linearly resamples non-24kHz inputs to 24,000 Hz.

```bash
# Navigate to demo folder
cd Demos/Mac_HSRU_Encodec

# Clear Apple Gatekeeper quarantine flag (for fresh downloads)
xattr -cr .

# Run end-to-end Audio Roundtrip (Encoder -> Quantizer -> Decoder)
./hsru_ggml models/codec_weights_fxp.gguf test.wav out.wav
```
*The synthesized waveform is saved directly to `out.wav`.*

---

### 💬 2. HSRU-Small (Autoregressive Language Generation)
A 26M parameter language model trained from scratch on the TinyStories corpus using pure HSRU recurrent equations.

* **Throughput:** **~130 tokens/second** on standard CPU.
* **Memory Profile:** Flat $\mathcal{O}(1)$ memory (no KV cache).
* **Decoupled:** Zero Python runtime; runs purely via native C++ pointer arithmetic.

```bash
# macOS
cd Demos/Mac_HSRU_Small
xattr -cr .
./hsru_edge

# Windows (Command Prompt or PowerShell)
cd Demos\Win_HSRU_Small
hsru_edge.exe

# Linux
cd Demos/Linux_HSRU_Small
chmod +x hsru_edge
./hsru_edge
```

---

### 🚁 3. HSRU-Drone (Predictive Anomaly Detection on UAVs)
A real-time edge anomaly detector running on high-frequency IMU telemetry from drone flight controllers. Uses predictive physics dynamics to catch propeller damage and motor failure immediately upon takeoff.

* **Parity:** Exact mathematical match with PyTorch training logs.
* **Accuracy:** 100% flight-level detection rate on propeller fault datasets (80/80 damaged flights caught, 0.0% false alarms with $K=3$).
* **Latency:** Sub-millisecond reaction time per telemetry frame (<25 µs in C++).
* **Detailed Metrics:** See [DRONE_METRICS.md](DRONE_METRICS.md) for benchmark tables, damage severity scaling, and persistence filter analysis.

```bash
cd Demos/Linux_HSRU_UAV
chmod +x hsru_drone
./hsru_drone
```

---

## 🔬 Benchmark Comparison: HSRU vs. Standard Transformers

| Metric | Standard Transformer (e.g. LLaMA / EnCodec) | HSRU (This Architecture) |
|---|---|---|
| **Inference Time Complexity** | $\mathcal{O}(T^2)$ or $\mathcal{O}(T \cdot \text{cache})$ | **$\mathcal{O}(T)$ Linear** |
| **Inference Memory (KV-Cache)** | Unbounded $\mathcal{O}(T)$ growth | **$\mathcal{O}(1)$ Strictly Flat** |
| **Max Context on 2GB RAM** | Drops / OOMs past ~4k tokens | **Virtually Infinite (Continuous)** |
| **Acoustic Waveform Modeling** | Prone to phase drift | **Snake1d Periodic Phase Coherence** |
| **Formal Safety Certification** | Mathematically Unbounded | **BIBO Convex Blending (Provable)** |
| **Edge Dependency Footprint** | Heavy (LibTorch / ONNX / CUDA) | **Zero-Dependency Native C++** |

---

## 🛠️ Troubleshooting and Platform Notes

* **macOS Gatekeeper Alert:** If macOS displays a *"cannot be opened because the developer cannot be verified"* alert on downloaded binaries, clear the quarantine attribute:
  ```bash
  xattr -cr .
  ```
* **Linux Execution Permissions:** If bash reports `Permission denied`, set the executable bit:
  ```bash
  chmod +x hsru_edge hsru_drone
  ```
* **CPU Architecture:** Pre-compiled Linux binaries are built for `x86_64` (AVX2/FMA). For ARM Linux (Raspberry Pi, Jetson), source compilation is available upon request.

---

## 📄 Intellectual Property and Evaluation Terms

* **Proprietary Technology:** The HSRU architecture design, PyTorch training pipelines, custom fused CUDA kernels, and native C++ engine source are the proprietary intellectual property of Sameer Humagain.
* **Permitted Evaluation Use:** The pre-compiled binary engines, model weights, and technical whitepapers in this public repository are provided strictly for evaluation, benchmarking, peer review, and technical verification. Reverse engineering, decompilation, or unauthorized commercial redistribution is not permitted.
* **Source Code Access & Collaboration:** The underlying source code is not published openly in this repository, but it is available upon request for:
  * **Academic & Research Collaborations:** Joint research, benchmark reproductions, and grant-backed investigations.
  * **Hardware & Pilot Integrations:** Testing HSRU on custom flight controllers (Pixhawk / PX4), edge DSPs, wearables, or embedded accelerators.
  * **Commercial Licensing:** Production deployments and specialized adaptations.

If you are interested in reviewing the source code, running custom training runs, or collaborating on scaling the architecture, please reach out directly:

* **Email:** [im@hsameer.com.np](mailto:im@hsameer.com.np?subject=HSRU%20Source%20Code%20Access%20and%20Collaboration)
* **GitHub:** [@hsameerc](https://github.com/hsameerc)
