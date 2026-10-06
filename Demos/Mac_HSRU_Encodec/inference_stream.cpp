// ============================================================================
// HSRUCodec Streaming Inference Engine
// Default: full-file mode (zero boundaries, cleanest audio).
// Usage: ./inference_stream <input.wav> [output.wav] [--stream [frames]]
// ============================================================================
#include "hsru_codec.h"
#include <cstdint>
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>
#include <cstring>

std::vector<float> read_wav_s(const std::string& filename) {
    std::ifstream file(filename, std::ios::binary);
    if (!file) throw std::runtime_error("Could not open WAV file");
    char chunk_id[5] = {0};
    uint32_t chunk_size = 0;
    file.read(chunk_id, 4);
    file.read(reinterpret_cast<char*>(&chunk_size), 4);
    file.read(chunk_id, 4);
    uint32_t data_size = 0;
    uint16_t audio_format = 1, num_channels = 1, bits_per_sample = 16;
    uint32_t sample_rate = 24000;
    while (file.read(chunk_id, 4)) {
        file.read(reinterpret_cast<char*>(&chunk_size), 4);
        if (std::string(chunk_id, 4) == "fmt ") {
            file.read(reinterpret_cast<char*>(&audio_format), 2);
            file.read(reinterpret_cast<char*>(&num_channels), 2);
            file.read(reinterpret_cast<char*>(&sample_rate), 4);
            file.seekg(6, std::ios::cur);
            file.read(reinterpret_cast<char*>(&bits_per_sample), 2);
            if (chunk_size > 16) file.seekg(chunk_size - 16, std::ios::cur);
        } else if (std::string(chunk_id, 4) == "data") {
            data_size = chunk_size; break;
        } else { file.seekg(chunk_size, std::ios::cur); }
    }
    if (data_size == 0) throw std::runtime_error("Could not find data chunk");
    std::vector<float> audio;
    if (audio_format == 3 && bits_per_sample == 32) {
        int n = data_size / sizeof(float); audio.resize(n);
        file.read(reinterpret_cast<char*>(audio.data()), data_size);
    } else if (audio_format == 1 && bits_per_sample == 16) {
        int n = data_size / sizeof(int16_t);
        std::vector<int16_t> pcm(n); audio.resize(n);
        file.read(reinterpret_cast<char*>(pcm.data()), data_size);
        for (int i = 0; i < n; ++i) audio[i] = pcm[i] / 32768.0f;
    } else { throw std::runtime_error("Unsupported WAV format."); }
    return audio;
}

int main(int argc, char** argv) {
    std::cout << "======================================\n";
    std::cout << "  HSRUCodec Edge Inference (Streaming)\n";
    std::cout << "======================================\n";
    if (argc < 2) {
        std::cerr << "Usage: ./inference_stream <input.wav> [output.wav] [--stream [frames]]\n";
        return 1;
    }
    std::string input_wav = argv[1];
    std::string output_wav = "output.wav";
    int chunk_frames = 0;
    for (int i = 2; i < argc; ++i) {
        if (std::strcmp(argv[i], "--stream") == 0) {
            chunk_frames = 100;
            if (i + 1 < argc) { int v = std::atoi(argv[i+1]); if (v > 0) { chunk_frames = v; ++i; } }
        } else { output_wav = argv[i]; }
    }
    void* ctx = hsru_codec_init_context("models/codec_weights.bin");
    if (!ctx) { std::cerr << "[ERROR] Failed to load weights\n"; return 1; }
    HSRUCodecHeader hdr;
    { std::ifstream hf("models/codec_weights.bin", std::ios::binary); hf.read(reinterpret_cast<char*>(&hdr), sizeof(hdr)); }
    int num_quantizers = hdr.num_quantizers;
    int downsample = hdr.downsample;
    int sample_rate = hdr.sample_rate;
    std::cout << "[1] Loading weights OK\n";
    std::vector<float> audio = read_wav_s(argv[1]);
    int num_samples = (int)audio.size();
    num_samples = (num_samples / downsample) * downsample;
    int num_frames = num_samples / downsample;
    if (chunk_frames <= 0) chunk_frames = num_frames;
    if (chunk_frames >= num_frames)
        std::cout << "[Mode] Full-file (no boundaries)\n";
    else
        std::cout << "[Mode] Streaming, chunk=" << chunk_frames << " frames\n";
    void* state = hsru_codec_create_state(ctx);
    std::vector<float> out_audio((size_t)num_samples);
    std::vector<int> codes((size_t)num_frames * num_quantizers);
    int chunk_samples = chunk_frames * downsample;
    auto t0 = std::chrono::high_resolution_clock::now();
    for (int t = 0; t < num_samples; t += chunk_samples) {
        int cur = std::min(chunk_samples, num_samples - t);
        cur = (cur / downsample) * downsample;
        if (cur == 0) break;
        int cf = cur / downsample, fo = t / downsample;
        hsru_codec_encode_stream(ctx, state, audio.data() + t, cur, codes.data() + fo * num_quantizers);
        hsru_codec_decode_stream(ctx, state, codes.data() + fo * num_quantizers, cf, out_audio.data() + t);
        std::cout << "\rProcessed " << t + cur << " / " << num_samples << " samples..." << std::flush;
    }
    auto t1 = std::chrono::high_resolution_clock::now();
    std::cout << "\n[TIMING] Total Streaming Engine Time: "
              << std::chrono::duration<double>(t1 - t0).count() << " s\n";
    hsru_codec_free_state(state);
    hsru_codec_free_context(ctx);
    std::ofstream out(output_wav, std::ios::binary);
    uint32_t data_bytes = (uint32_t)num_samples * sizeof(int16_t);
    uint32_t riff_size = 36 + data_bytes;
    uint16_t af = 1, nc = 1, ba = sizeof(int16_t), bi = 16;
    uint32_t br = (uint32_t)sample_rate * sizeof(int16_t), fs = 16;
    out.write("RIFF",4); out.write((char*)&riff_size,4); out.write("WAVE",4);
    out.write("fmt ",4); out.write((char*)&fs,4); out.write((char*)&af,2); out.write((char*)&nc,2);
    out.write((char*)&sample_rate,4); out.write((char*)&br,4); out.write((char*)&ba,2); out.write((char*)&bi,2);
    out.write("data",4); out.write((char*)&data_bytes,4);
    std::vector<int16_t> pcm((size_t)num_samples);
    for (int i = 0; i < num_samples; ++i) {
        float v = std::max(-1.0f, std::min(1.0f, out_audio[i]));
        pcm[i] = static_cast<int16_t>(v * 32767.0f);
    }
    out.write((char*)pcm.data(), data_bytes);
    std::cout << "\n[SUCCESS] Audio saved to " << output_wav << "\n";
    return 0;
}
