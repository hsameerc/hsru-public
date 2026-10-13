# HSRU LLM Edge SDK

Welcome to the **HSRU LLM True Black Box SDK**. This directory contains everything you need to run your fine-tuned HSRU Large Language Model natively on edge devices (Windows, Linux, macOS, or Raspberry Pi) with **Zero Dependencies**.

## 🎯 Target Build Information

| Property | Specification |
|:---|:---|
| **Target OS** | **`Windows`** |
| **Architecture** | **`x86_64 (AMD64)`** |
| **Intended Hardware** | **`Windows 10 / Windows 11 (64-bit)`** |
| **Static Linkage** | **✅ Enabled** (Standalone binary has ZERO external runtime dependencies) |

> 📌 **Compatibility Summary:** - **Windows Deployment:** This SDK was compiled on Windows. It statically links `libgcc`, `libstdc++`, and `libwinpthread` (OpenMP), meaning it has ZERO external dependencies and will run perfectly out of the box on any 64-bit Windows machine.

## 🌟 Key Features

1. **True Black Box Security:** The proprietary neural network architectures (`hsru_math.cpp`, `hsru_llm.cpp`) are compiled into binary archives (`libhsru_llm.so`, `libhsru_llm.a`). No C++ source code is exposed, keeping intellectual property safe.
2. **Zero Dependencies:** The standalone executable (`./hsru_edge`) is **statically linked**. It runs right out of the box on a fresh OS install without Python, PyTorch, HuggingFace, CUDA, or runtime libraries.
3. **Ultra Lightweight:** The total deployment size is reduced by over 5GB compared to standard frameworks. The entire runtime fits in just a few dozen megabytes.

## 📂 Directory Structure

```
.
├── hsru_edge                   # Standalone C++ executable (Zero Dependencies)
├── models/
│   ├── story_weights.bin       # Exported model weights (FP32 or INT8)
│   └── story_manifest.json     # Byte offsets and tensor shapes
├── vocab/                      # BPE/HF Tokenizer logic
├── libhsru_llm.so              # Compiled Black Box inference shared library
├── libhsru_llm.a               # Static binary archive for native re-linking
├── rebuild_lib.sh              # 1-second native shared library linker for Raspberry Pi / Edge
├── Makefile                    # Edge compilation build targets (make / make lib)
├── assistant_controller.py     # Example Python frontend (UI/STT/TTS)
├── test_api.py                 # Example local REST API server
├── setup_audio.sh              # (Optional) Installs offline voice TTS/STT binaries
└── README.md                   # This file
```

## 🍓 Raspberry Pi & Linux Edge Quickstart

### Route 1: Standalone C++ Engine (Recommended — Zero Dependencies)
Run the pre-compiled binary directly without Python, PyTorch, or CUDA:

**On Linux / Raspberry Pi / macOS:**
```bash
./hsru_edge
```

**On Windows:**
```bash
.\hsru_edge.exe
```

> **Zero GLIBC Issues:** The executable is pre-compiled with full static linkage. It runs out of the box on Raspberry Pi 3/4/5, Jetson, and any Linux distribution without needing matching GLIBC versions or external packages.

---

### Route 2: Python Frontend (REST API & Terminal Assistant)
If you prefer running Python wrappers (`test_api.py`, `assistant_controller.py`):

```bash
pip install -r requirements.txt
python3 test_api.py             # Start local REST API server
python3 assistant_controller.py # Start interactive assistant
```

#### Optional: Local Offline Voice Support (STT & TTS)
To give your assistant offline listening and speech capabilities:
```bash
chmod +x setup_audio.sh
./setup_audio.sh
python3 assistant_controller.py
```

---

### 🔧 Troubleshooting: Linux / Raspberry Pi `GLIBC_X.XX not found` or `libm.so.6` Error
If you cross-compiled on a modern host (e.g. Windows WSL with Ubuntu 24.04 / GLIBC 2.39+) and copied this folder to a Raspberry Pi running Debian (Bookworm/Bullseye with older GLIBC), Python's dynamic linker may report:
```
OSError: /lib/aarch64-linux-gnu/libm.so.6: version 'GLIBC_2.43' not found (required by libhsru_llm.so)
```

**Instant Fix (Takes < 1 second on Raspberry Pi):**
The static engine archive `libhsru_llm.a` is included. You can instantly link it natively on the Raspberry Pi:

```bash
# 1. Install prerequisites on Raspberry Pi:
sudo apt update && sudo apt install -y build-essential libgomp1

# 2. Run the 1-second rebuild script (or run `make lib`):
./rebuild_lib.sh
```
This generates a fresh `libhsru_llm.so` tied to your Raspberry Pi's exact system C library in under one second. Then re-run `python3 test_api.py` or `python3 assistant_controller.py`.

---

## ⚙️ Technical Details
- **Windows Deployment:** This SDK was compiled on Windows. It statically links `libgcc`, `libstdc++`, and `libwinpthread` (OpenMP), meaning it has ZERO external dependencies and will run perfectly out of the box on any 64-bit Windows machine.
- **Quantization:** If exported with `--fxp`, the weights are stored in INT8 precision, cutting RAM usage and bandwidth in half.
