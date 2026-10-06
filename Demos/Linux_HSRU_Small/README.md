# HSRU Edge Deployment

This folder contains everything you need to run your fine-tuned HSRU model on edge devices (Windows, Linux, or Raspberry Pi) with extremely minimal dependencies.

## 1. The Lightweight Python Route (Recommended)
If you want to use the provided Python wrapper (`assistant_controller.py`), you only need Python and NumPy.
```bash
pip install -r requirements.txt
python assistant_controller.py
```
**Note:** You do NOT need PyTorch, CUDA, or HuggingFace installed! This saves over 5GB of space.

### Optional: Voice Support (Linux/macOS)
If you want the assistant to speak and listen, run `./setup_audio.sh` first to download the tiny local TTS/STT binaries.

## 2. The Truly Zero-Dependency Route (No Python)
If you want to run this on a completely blank machine without even installing Python:
1. You must write a pure C++ `main.cpp` loop to handle the user text input yourself.
2. Compile it statically into a `.exe` (Windows) or an ELF binary (Linux/Raspberry Pi) using your C++ compiler.
3. Copy that compiled executable and the `model.bin` to the blank target machine. It will run out of the box.