# HSRUCodec Codec  Edge SDK

Copy this folder to any Linux/macOS device and run instantly:

```bash
make && ./demo
```

## Structure

```
.
 models/
    codec_weights.bin      82.9 MB  INT8 (fxp)
    codec_manifest.json    tensor shapes + byte offsets
 include/
    hsru_codec.h           C++ header (HSRUCodecHeader + weight structs)
 lib/
    libhsru_audio.so       HSRU block engine
 Makefile
 demo.cpp                 Basic header check example
 inference.cpp            Minimal wrapper to call the DLL
 test.wav                 Example 24kHz audio file
 README.md
```

## Quick Start

```bash
# 1. Compile the C++ wrappers
make

# 2. Run the basic header diagnostic
./demo

# 3. Process the example audio
./inference test.wav output.wav
```


## Binary Format

Header: 12  int32 (48 bytes).  See `HSRUCodecHeader` in hsru_codec.h.
All weights follow in the order listed in `models/codec_manifest.json`.

Precision: **INT8 (fxp)**
INT8 format: each tensor preceded by a float32 scale factor. Dequantize: w = int8_val * scale

## Integration

Load `models/codec_manifest.json` to get the byte offset and shape of every
tensor, then fread or mmap into the hsru-dynamic codec engine structs.

The engine requires:
- `memory_forward_step()` / `logic_forward_step()`  from libhsru_audio.so
- Conv1d / ConvTranspose1d  strided audio downsampling/upsampling
- RVQ encode/decode  12 codebook levels  1024 codes  64-dim projection
- Snake activation: `x + (1/alpha) * sin(alpha*x)^2`
- LayerNorm  pre-quantization normalization

##   Note

This is **codec binary v2**.  The LLM binary (`audio_weights.bin`) is **v1** 
different format, incompatible.  Both share `libhsru_audio.so` for the
HSRU block step functions.
