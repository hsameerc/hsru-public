<div align="center">
  <h1>HSRU: Hybrid State Recurrent Unit</h1>
  <h3>A constant-memory recurrent architecture for on-device AI, tested on text, audio and sensor telemetry</h3>
</div>

---

## Summary

Transformers keep a Key-Value cache that grows with every token or frame they process. On laptops, phones, embedded boards and edge chips, that growing cache is what eventually causes memory pressure, thermal throttling and latency spikes.

HSRU is a recurrent unit that combines leaky integrate-and-fire dynamics, discrete threshold gates and continuous gated pathways. Like other recurrent and state-space models, it carries a fixed-size state instead of a cache, so:

1. **Memory is constant (O(1))** for the whole run, whether it lasts 10 seconds or 10 hours.
2. **Time is linear (O(T))**, with the same cost per token or frame.
3. **One core handles several modalities.** The same unit is used here for language tokens, 24 kHz audio and 100 Hz IMU telemetry.

All models in this repository were trained on a **single 12 GB consumer NVIDIA GPU**, which is why they are small (26M to 83M parameters).

---

## What is in this repository

| Component | Status | Location |
|---|:---:|---|
| Mathematical derivations and stability analysis | Open | [Whitepapers/](Whitepapers/) |
| Pre-compiled demo binaries + model weights | Public, for evaluation | [Demos/](Demos/) |
| Benchmark logs and metrics | Open | [DRONE_METRICS.md](DRONE_METRICS.md), [TRAINING_METRICS.md](TRAINING_METRICS.md), [Metrics/](Metrics/) |
| PyTorch training framework | Proprietary | Available to research and pilot partners |
| Fused CUDA kernels | Proprietary | Available to research and pilot partners |
| C++ inference engine source | Proprietary | Available under collaboration or licensing |

The math is open so it can be checked. The binaries let anyone measure speed and memory without installing Python, PyTorch or CUDA. The implementation source is shared with research collaborators, pilot partners and licensees.

---

## Demos

No Python, PyTorch or CUDA is needed to run them.

| Demo | Modality | macOS (Apple Silicon) | Linux (ARM64: Raspberry Pi, Jetson) | Windows (x64) |
|---|---|:---:|:---:|:---:|
| **HSRU-Encodec** | 24 kHz neural audio codec | Yes | Available upon request | Available upon request |
| **HSRU-Small** | 26M language model | Yes | Yes | Yes |
| **HSRU-Drone** | IMU fault detection | Available upon request | Yes | Available upon request |

The C++ inference runtime has zero external dependencies and compiles across macOS, Linux (x86_64 and ARM64), and Windows. Pre-compiled binaries for platforms not bundled in this public release (such as Drone for macOS/Windows, Audio for Linux/Windows, and Linux x86_64 builds) are available upon request to keep the initial repository clone lightweight.

### Verify the downloads

Every file in `Demos/` is listed in [Demos/SHA256SUMS](Demos/SHA256SUMS). The macOS binaries are code-signed and all binaries are symbol-stripped.

```bash
cd Demos
shasum -a 256 -c SHA256SUMS          # macOS
sha256sum -c SHA256SUMS              # Linux
```
On Windows (PowerShell): `Get-FileHash .\Win_HSRU_Small\hsru_edge.exe -Algorithm SHA256`, then compare with the entry in `SHA256SUMS`.

---

### 1. HSRU-Encodec (neural audio codec)

An 82.6M parameter encoder, residual quantizer and decoder for 24 kHz mono audio.

| Metric | Value (printed by the binary) |
|---|---|
| Bitrate | 9 kbps (75 frames/s, 12 codebooks, 10 bits each) |
| Speed | ~4x faster than real time on an Apple Silicon CPU (RTF 0.21 to 0.24) |
| Reconstruction correlation | ~0.93 (Pearson, vs. original) |
| SNR | ~8.7 to 8.9 dB |
| Compute buffers | ~290 MB encoder / ~267 MB decoder, allocated once |
| Weights | INT8 GGUF, 97 MB |

The architecture follows a convolutional encoder/decoder design similar to EnCodec, with HSRU blocks as the sequence model. It uses periodic Snake activations, as introduced in prior work (BigVGAN, DAC). A comparison against EnCodec at matching bitrates is planned (see [Next phase](#next-phase)).

```bash
cd Demos/Mac_HSRU_Encodec
xattr -cr .        # clear the Gatekeeper quarantine flag on downloaded files
./hsru_ggml models/codec_weights_fxp.gguf test.wav out.wav
```

---

### 2. HSRU-Small (language model)

A 26.6M parameter language model trained from scratch on TinyStories, with the GPT-2 tokenizer (50,257 tokens).

| Metric | Value |
|---|---|
| Best validation loss | 1.23 (perplexity ~3.4), step 16,000 |
| Generation speed | ~120 to 130 tokens/s on an Apple Silicon CPU |
| Recurrent state memory | ~6 MB flat RAM across all 12 layers (zero token KV cache) |
| INT8 weights size | 25 MB |

Unlike standard Transformers that store past token keys and values in an expanding KV cache (O(T) RAM growth), HSRU updates a fixed-size Product-Key Memory (PKM) associative grid in-place. State memory is allocated once at startup and remains strictly O(1) constant regardless of stream length.

```bash
# macOS
cd Demos/Mac_HSRU_Small && xattr -cr . && ./hsru_edge

# Linux ARM64 (Raspberry Pi / Jetson)
cd Demos/Linux_HSRU_Small && chmod +x hsru_edge && ./hsru_edge

# Windows
cd Demos\Win_HSRU_Small
hsru_edge.exe
```

#### Scalability: 536M Foundation Pretraining
Beyond the bundled 26M demo, the architecture was scaled to a 536M parameter model (24 modules, 1024 hidden dim, 4096 logic dim, 128 PKM codes) and pretrained over 24,400 steps on diverse web corpora (40% FineWeb-Edu, 20% English Wikipedia, 15% SlimPajama-6B, 10% CodeParrot, 10% TinyStories, 5% OpenHermes-2.5):
* **Convergence:** Validation loss converged from 10.9 down to 2.53 without gradient instability or loss spikes.
* **PKM state & memory footprint:** With INT8 weight quantization, the weights file is 463 MB. The fixed FP16 PKM state grid occupies 768 MB, giving a flat runtime RAM footprint of ~1.23 GB on CPU.
* **Speed:** Generates ~45 tokens/second on an Apple Silicon CPU without GPU acceleration (0 memory leaks).
* *The 536M pre-compiled binary and checkpoint are available upon request for prospective partners and evaluators (omitted from the repository archive to keep download sizes lightweight).*

---

### 3. HSRU-Drone (IMU fault detection)

An unsupervised next-step predictor trained only on healthy flights. Damage is flagged when prediction error stays above a calibrated threshold. It was evaluated on the **UAV Realistic Fault Dataset (ICRA 2023)**: 99 quadrotor flights, 6-axis IMU at **100 Hz**.

| Metric | Result |
|---|---|
| Damaged flights detected (K=3 persistence) | 80 / 80 |
| False alarms on held-out normal flights | 0 / 3 (small sample, see limitations) |
| Window-level AUROC | 0.87 to 0.89 depending on damage class |
| Error increase vs. normal | 51x (1 broken blade) to 171x (4 broken blades) |
| C++ inference time | <25 µs per frame on CPU |

Full tables and method: [DRONE_METRICS.md](DRONE_METRICS.md).

```bash
cd Demos/Linux_HSRU_UAV
chmod +x hsru_drone
./hsru_drone
```

---

## Architecture overview

```text
Input x[t]
   │
   ├─ Fused linear projections (leak, shunt, soma, dendrites)
   ├─ Dendritic integration (event detection)
   ├─ Split recurrent memory
   │    ├─ half the channels: spiking (threshold) mode
   │    └─ half the channels: continuous leaky mode
   └─ Gated (GLU) logic layer + sinusoidal clock
   │
Output h[t]
```

* **Spiking channels** use discrete thresholds, so they fire sparsely and only when events happen.
* **Continuous channels** integrate floating-point state for smooth context.
* **Blend mode** mixes the memory and logic paths with a convex weight β ∈ [0, 1], which keeps the recurrent state bounded (derivation in the whitepapers).

### Stability

* **Bounded state (BIBO):** with convex blending, bounded inputs give bounded internal state. See [hsru_mathematics.pdf](Whitepapers/hsru_mathematics.pdf) and [hsru_verification.pdf](Whitepapers/hsru_verification.pdf).
* **Deterministic execution:** the edge runtimes use bounded approximations and no data-dependent loops, so per-step time is predictable. This was designed with DO-178C-style constraints in mind. **It is not certified.**

---

## Limitations and what is not claimed

* **No claim of beating Transformers on quality.** The claims here are constant memory, a working edge runtime and results in three domains.
* **Constant memory is not unique to HSRU.** LSTMs, Mamba, RWKV and other recurrent/state-space models share it. Head-to-head comparisons are next phase.
* **Model scale.** Public demo binaries are bundled at lightweight edge scale (26M to 83M) for instant local testing. While the architecture has been trained up to 536M parameters on FineWeb-Edu and Wikipedia (24,400 steps, stable 2.53 validation loss), behaviour at multi-billion parameter frontier scale (7B+) has not been evaluated.
* **Long-range exact recall** (needle-in-a-haystack tasks) is a known weakness of fixed-state models and has not been evaluated yet.
* **Drone false-alarm evidence is thin:** 0 false alarms on 3 held-out normal flights. Rotating the held-out flights (cross-validation over all 19 normal flights) is next phase.
* **Platform coverage is partial** (see the demo table).
* The papers in `Whitepapers/` are self-published and have not been peer reviewed.

---

## Next phase

* Same-size Transformer and Mamba/RWKV baselines trained under identical settings on TinyStories
* Evaluation against the published TinyStories models on the full validation set
* EnCodec comparison at 6 and 12 kbps on a standard speech/music test set (SNR, mel distance, ViSQOL/PESQ)
* Leave-flights-out cross-validation for drone false-alarm rates
* On-device timing on microcontrollers (STM32 / Pixhawk) and Raspberry Pi
* x86_64 Linux and Windows builds for all demos
* Scaling beyond 100M parameters and long-context recall tests

---

## Collaboration

I built HSRU on my own, from the equations to the C++ runtimes. I'm based in Australia and open to working with companies and engineering teams who want to take it further, through technology acquisition / joining a team, or commercial licensing.

Technical questions, evaluation requests and partnership inquiries are handled by email.

| | |
|---|---|
| **Author** | Sameer Humagain |
| **Email** | [im@hsameer.com.np](mailto:im@hsameer.com.np?subject=HSRU) |
| **GitHub** | [@hsameerc](https://github.com/hsameerc) |

---

## Troubleshooting

* **macOS "cannot be opened because the developer cannot be verified":** run `xattr -cr .` inside the demo folder.
* **Linux `Permission denied`:** run `chmod +x hsru_edge hsru_drone`.
* **Linux `Exec format error`:** the Linux binaries are ARM64. They will not run on x86_64 PCs.

---

## Intellectual property and evaluation terms

* The HSRU architecture design, PyTorch training pipelines, CUDA kernels and C++ engine source are the proprietary intellectual property of Sameer Humagain.
* The binaries, model weights and whitepapers in this repository are provided for evaluation, benchmarking, peer review and technical verification. Reverse engineering, decompilation and commercial redistribution are not permitted.
* Source access is available on request for academic collaborations, hardware pilots and commercial licensing: [im@hsameer.com.np](mailto:im@hsameer.com.np?subject=HSRU%20Source%20Access).
