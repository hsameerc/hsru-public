# HSRUCodec Codec Edge SDK

Welcome to the **HSRUCodec HSRU Encodec True Black Box SDK**. This directory contains the fully self-contained edge deployment for the HSRU audio codec.

## 🌟 Key Features

1. **True Black Box Security:** The neural network source code has been entirely scrubbed. The architecture is safely encapsulated within `libhsru_codec` libraries. Your intellectual property is protected.
2. **Zero Dependency:** There is no need for Python, PyTorch, or CUDA. Parallelization libraries (like `libomp`) are statically compiled directly into the binary. 
3. **Real-time Streaming:** The SDK supports ultra-low latency, real-time chunked streaming of audio frames.

## 📂 Directory Structure

```
.
├── models/
│   ├── codec_weights.bin       # 82.9 MB  [INT8 (fxp)] Weights file
│   └── codec_manifest.json     # Tensor shapes and byte offsets
├── include/
│   └── hsru_codec.h            # Public C-API function signatures
├── lib/
│   └── libhsru_codec.so        # The compiled Black Box core engine (or .dylib / .dll)
├── demo                        # Pre-compiled executable for basic sanity checks
├── inference                   # Pre-compiled executable for full-file WAV conversion
├── inference_stream            # Pre-compiled executable for chunked streaming WAV conversion
├── test.wav                    # Example 24kHz audio file
└── README.md                   # This file
```

## 🚀 Quick Start

Run the executables directly from the terminal. No installation required!

```bash
# 1. Run the basic header diagnostic check
./demo

# 2. Process an entire audio file (Full-file mode)
./inference test.wav output.wav

# 3. Process the audio file using the real-time streaming engine
./inference_stream test.wav stream_out.wav --stream 100
```

## ⚙️ Integration (C-API)

To integrate this codec into your own application (e.g. a VoIP client):
1. Include `include/hsru_codec.h` in your project.
2. Link your application against `libhsru_codec`.
3. Use `hsru_codec_encode_stream` and `hsru_codec_decode_stream` in your audio callback loop.

## 🔧 Technical Specifications
- **Precision:** INT8 (fxp)
- **Architecture:** 8 Encoder Blocks, 8 Decoder Blocks
- **RVQ Configuration:** 12 Codebooks, 1024 codes each
- **Sample Rate:** 24000 Hz (Downsample Factor: 320)
- **macOS Compatibility:** Binaries are explicitly compiled for `macOS 11.0+` with static `libomp` to ensure seamless execution on any modern Mac.

*Note: This is codec binary v2. The LLM binary is v1 format and is incompatible with this engine.*
