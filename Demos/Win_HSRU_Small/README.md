# HSRU LLM Edge SDK

Welcome to the **HSRU LLM True Black Box SDK**. This directory contains everything you need to run your fine-tuned HSRU Large Language Model natively on edge devices (Windows, Linux, macOS, or Raspberry Pi) with **Zero Dependencies**.

## 🌟 Key Features

1. **True Black Box Security:** The proprietary neural network architectures (like `hsru_math.cpp` and `hsru_llm.cpp`) have been fully compiled into the distributed binary object (`libhsru_llm.so` / `.dylib` / `.dll`). No source code is exposed, making your intellectual property perfectly safe for client distribution.
2. **Zero Dependency:** There is absolutely no need for Python, PyTorch, HuggingFace, or CUDA. The OpenMP acceleration library (`libomp`) has been **statically linked**, meaning it's bundled directly into the binary. It works right out of the box on a fresh OS install.
3. **Ultra Lightweight:** By removing all the bloated AI training dependencies, the total deployment size is reduced by over 5GB. The entire runtime fits in just a few dozen megabytes.

## 📂 Directory Structure

```
.
├── models/
│   ├── story_weights.bin       # The exported model weights (FP32 or INT8)
│   └── story_manifest.json     # Byte offsets and tensor shapes
├── vocab/                      # BPE/HF Tokenizer logic
├── libhsru_llm.so              # The compiled Black Box inference engine
├── assistant_controller.py     # Example Python frontend (UI/STT/TTS)
├── test_api.py                 # Example local API server
├── setup_audio.sh              # (Optional) Installs offline voice TTS/STT binaries
└── README.md                   # This file
```

## 🚀 Quick Start (Python Frontend Route)

If you have Python installed, you can use our lightweight wrappers which interface with the Black Box C++ engine via `ctypes`.

```bash
pip install -r requirements.txt
python test_api.py             # Start a local REST API
python assistant_controller.py # Start the interactive terminal assistant
```

### Optional: Local Voice Support (Linux/macOS)
To give your assistant the ability to listen and speak entirely offline:
```bash
chmod +x setup_audio.sh
./setup_audio.sh
python assistant_controller.py
```

## 🛠 True Zero-Dependency Route (C++ Only)

We have provided a complete standalone C++ entrypoint (`main.cpp`) that natively handles model execution and text decoding.

To compile and run the interactive C++ demo:

**For Windows:**
```bash
make
.\hsru_edge.exe
```

**For Linux / macOS:**
```bash
./build.sh
./hsru_edge
```

## ⚙️ Technical Details
- **Windows Deployment:** This SDK was compiled on Windows. It statically links `libgcc`, `libstdc++`, and `libwinpthread` (OpenMP), meaning it has ZERO external dependencies and will run perfectly out of the box on any Windows machine.
- **Quantization:** If exported with `--fxp`, the weights are stored in INT8 precision, further cutting RAM usage and bandwidth bottlenecks in half.
