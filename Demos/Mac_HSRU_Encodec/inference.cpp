// ============================================================================
// Phase 7: HSRU Codec Edge Inference Engine (Wrapper)
// ============================================================================
#include "hsru_codec.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <string>

// --- 5. Robust WAV Parser ---
std::vector<float> read_wav(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) throw std::runtime_error("Could not open WAV file");
    
    char chunk_id[5] = {0};
    uint32_t chunk_size = 0;
    
    file.read(chunk_id, 4);
    file.read(reinterpret_cast<char*>(&chunk_size), 4);
    file.read(chunk_id, 4); // "WAVE"
    
    uint32_t data_size = 0;
    uint16_t audio_format = 1;
    uint16_t num_channels = 1;
    uint32_t sample_rate = 24000;
    uint16_t bits_per_sample = 16;
    
    while (file.read(chunk_id, 4)) {
        file.read(reinterpret_cast<char*>(&chunk_size), 4);
        if (std::string(chunk_id, 4) == "fmt ") {
            file.read(reinterpret_cast<char*>(&audio_format), 2);
            file.read(reinterpret_cast<char*>(&num_channels), 2);
            file.read(reinterpret_cast<char*>(&sample_rate), 4);
            file.seekg(6, std::ios::cur); // Byte rate, block align
            file.read(reinterpret_cast<char*>(&bits_per_sample), 2);
            if (chunk_size > 16) file.seekg(chunk_size - 16, std::ios::cur);
        } else if (std::string(chunk_id, 4) == "data") {
            data_size = chunk_size;
            break;
        } else {
            file.seekg(chunk_size, std::ios::cur);
        }
    }
    
    if (data_size == 0) throw std::runtime_error("Could not find data chunk");
    
    std::vector<float> audio;
    if (audio_format == 3 && bits_per_sample == 32) {
        int num_samples = data_size / sizeof(float);
        audio.resize(num_samples);
        file.read(reinterpret_cast<char*>(audio.data()), data_size);
    } else if (audio_format == 1 && bits_per_sample == 16) {
        int num_samples = data_size / sizeof(int16_t);
        std::vector<int16_t> pcm(num_samples);
        file.read(reinterpret_cast<char*>(pcm.data()), data_size);
        audio.resize(num_samples);
        for (int i = 0; i < num_samples; ++i) audio[i] = pcm[i] / 32768.0f;
    } else {
        throw std::runtime_error("Unsupported WAV format. Only 16-bit PCM or 32-bit Float supported.");
    }
    return audio;
}

int main(int argc, char** argv) {
    std::cout << "======================================\n";
    std::cout << "  HSRUCodec Edge Inference (Phase 7)\n";
    std::cout << "======================================\n";
    if (argc < 2) { std::cerr << "Usage: ./inference <input.wav> [output.wav]\n"; return 1; }

    std::string input_wav  = argv[1];
    std::string output_wav = (argc >= 3) ? argv[2] : "output.wav";

    std::cout << "[1] Loading Codec weights from models/codec_weights.bin...\n";
    void* ctx = hsru_codec_init_context("models/codec_weights.bin");
    if (!ctx) { std::cerr << "[ERROR] Failed to load weights\n"; return 1; }

    // Read num_quantizers and downsample from the binary header
    HSRUCodecHeader hdr;
    {
        std::ifstream hf("models/codec_weights.bin", std::ios::binary);
        hf.read(reinterpret_cast<char*>(&hdr), sizeof(hdr));
    }
    int num_quantizers = hdr.num_quantizers;
    int downsample     = hdr.downsample;
    int sample_rate    = hdr.sample_rate;

    std::cout << "[2] Parsing " << input_wav << "...\n";
    std::vector<float> audio = read_wav(input_wav);
    int num_samples = (int)audio.size();
    int num_frames  = num_samples / downsample;

    std::cout << "[3] Running Encoder (convs + HSRU + RVQ)...\n";
    std::vector<int> codes((size_t)num_frames * num_quantizers);
    hsru_codec_encode(ctx, audio.data(), num_samples, codes.data());

    std::cout << "[4] Running Decoder (RVQ + HSRU + convs)...\n";
    // Decoder output length matches input after conv-transpose upsampling
    int out_samples = num_frames * downsample;
    std::vector<float> out_audio((size_t)out_samples);
    hsru_codec_decode(ctx, codes.data(), num_frames, out_audio.data());

    hsru_codec_free_context(ctx);

    // Write 16-bit PCM WAV
    std::cout << "[5] Writing " << output_wav << "...\n";
    std::ofstream out(output_wav, std::ios::binary);
    if (!out) { std::cerr << "[ERROR] Cannot open output file\n"; return 1; }
    {
        uint32_t data_bytes  = (uint32_t)out_samples * sizeof(int16_t);
        uint32_t riff_size   = 36 + data_bytes;
        uint16_t audio_fmt   = 1;        // PCM
        uint16_t num_ch      = 1;        // mono
        uint32_t byte_rate   = (uint32_t)sample_rate * sizeof(int16_t);
        uint16_t block_align = sizeof(int16_t);
        uint16_t bits        = 16;
        uint32_t fmt_size    = 16;
        // RIFF chunk
        out.write("RIFF", 4);
        out.write(reinterpret_cast<const char*>(&riff_size),   4);
        out.write("WAVE", 4);
        // fmt  sub-chunk
        out.write("fmt ", 4);
        out.write(reinterpret_cast<const char*>(&fmt_size),    4);
        out.write(reinterpret_cast<const char*>(&audio_fmt),   2);
        out.write(reinterpret_cast<const char*>(&num_ch),      2);
        out.write(reinterpret_cast<const char*>(&sample_rate), 4);
        out.write(reinterpret_cast<const char*>(&byte_rate),   4);
        out.write(reinterpret_cast<const char*>(&block_align), 2);
        out.write(reinterpret_cast<const char*>(&bits),        2);
        // data sub-chunk
        out.write("data", 4);
        out.write(reinterpret_cast<const char*>(&data_bytes),  4);
        // Samples
        std::vector<int16_t> pcm((size_t)out_samples);
        for (int i = 0; i < out_samples; ++i) {
            float v = std::max(-1.0f, std::min(1.0f, out_audio[i]));
            pcm[i]  = static_cast<int16_t>(v * 32767.0f);
        }
        out.write(reinterpret_cast<const char*>(pcm.data()), data_bytes);
    }
    out.close();

    std::cout << "\n[SUCCESS] Reconstructed audio saved to " << output_wav << "\n";
    return 0;
}
