#!/bin/bash
echo "========================================"
echo " HSRU Audio Engine Installer "
echo "========================================"

mkdir -p bin models/stt models/tts

echo "\n[1/3] Downloading Whisper STT Model..."
if [ ! -f "models/stt/ggml-tiny.en.bin" ]; then
    curl -L -o models/stt/ggml-tiny.en.bin https://huggingface.co/ggerganov/whisper.cpp/resolve/main/ggml-tiny.en.bin
else
    echo "STT Model already exists."
fi

echo "\n[2/3] Downloading Piper TTS Voice..."
if [ ! -f "models/tts/en_US-lessac-low.onnx" ]; then
    curl -L -o models/tts/en_US-lessac-low.onnx https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx
    curl -L -o models/tts/en_US-lessac-low.onnx.json https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/low/en_US-lessac-low.onnx.json
else
    echo "TTS Voice already exists."
fi

echo "\n[3/3] Installing Binaries (Whisper & Piper)..."

# Whisper.cpp (Build from source for maximum compatibility on Edge/Pi)
if [ ! -f "bin/whisper-cpp" ]; then
    echo "Building Whisper.cpp from source..."
    git clone https://github.com/ggerganov/whisper.cpp.git temp_whisper
    cd temp_whisper
    make -j4
    cp main ../bin/whisper-cpp
    cd ..
    rm -rf temp_whisper
fi

# Piper TTS (Download pre-compiled binary based on OS/Arch)
if [ ! -f "bin/piper" ]; then
    OS=$(uname -s)
    ARCH=$(uname -m)
    
    PIPER_URL=""
    if [ "$OS" = "Linux" ]; then
        if [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
            PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_aarch64.tar.gz"
        else
            PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_linux_x86_64.tar.gz"
        fi
    elif [ "$OS" = "Darwin" ]; then
        PIPER_URL="https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_macos_x86_64.tar.gz"
    fi
    
    if [ -n "$PIPER_URL" ]; then
        echo "Downloading Piper for $OS $ARCH..."
        curl -L -o piper.tar.gz $PIPER_URL
        tar -xf piper.tar.gz
        cp piper/piper bin/
        cp piper/piper_phonemize bin/
        rm -rf piper piper.tar.gz
    else
        echo "Warning: Could not determine Piper binary for $OS $ARCH. Please install manually."
    fi
fi

chmod +x bin/*
echo "\nAudio Setup Complete! You can now run python3 assistant_controller.py with full voice capabilities."
