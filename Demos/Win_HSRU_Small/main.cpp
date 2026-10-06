#include "hsru_llm.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <chrono>
#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <cstring>
#include <ctime>

int main(int argc, char* argv[]) {
    std::cout << "--- HSRU Edge LLM Engine ---\n";
    const char* bin_path = "models/story_weights.bin";
    const char* vocab_path = "models/vocab.txt";

    if (argc > 1) bin_path = argv[1];
    if (argc > 2) vocab_path = argv[2];

    std::cout << "[INFO] Loading model from " << bin_path << "...\n";
    void* ctx = hsru_llm_init_context(bin_path);
    if (!ctx) {
        std::cerr << "Failed to initialize context from " << bin_path << "\n";
        return 1;
    }

    int vocab_size = hsru_llm_get_vocab_size(ctx);
    std::cout << "[INFO] Loading vocab from " << vocab_path << "... (Vocab Size: " << vocab_size << ")\n";
    char** vocab = (char**)calloc(vocab_size, sizeof(char*)); // zeroed: safe to free unfilled slots
    FILE* vfile = fopen(vocab_path, "r");
    if (!vfile) {
        std::cerr << "Failed to open vocab\n";
    } else {
        char line[256];
        int v_idx = 0;
        while (fgets(line, sizeof(line), vfile) && v_idx < vocab_size) {
            // Remove trailing newline
            size_t len = strlen(line);
            if (len > 0 && line[len-1] == '\n') {
                line[len-1] = '\0';
                len--;
            }
            if (len > 0 && line[len-1] == '\r') {
                line[len-1] = '\0';
                len--;
            }
            
            // Allocate string
            vocab[v_idx] = (char*)malloc(len + 1);
            strcpy(vocab[v_idx], line);
            
            // Replace "\\n" with actual newline
            char* pos = vocab[v_idx];
            while ((pos = strstr(pos, "\\n")) != nullptr) {
                *pos = '\n';
                memmove(pos + 1, pos + 2, strlen(pos + 2) + 1);
                pos++;
            }
            v_idx++;
        }
        fclose(vfile);
    }

    std::cout << "[INFO] Generation Started...\n\n";
    srand((unsigned)time(NULL));
    int current_token = 50256; // <|endoftext|> for TinyStories
    
    auto start_time = std::chrono::high_resolution_clock::now();
    int gen_length = 200;
    
    float* logits = (float*)malloc(vocab_size * sizeof(float));
    int* generated_tokens = (int*)malloc(gen_length * sizeof(int));
    int num_generated = 0;
    
    struct TokenProb { float prob; int id; };
    TokenProb* token_probs = (TokenProb*)malloc(vocab_size * sizeof(TokenProb));

    for (int t = 0; t < gen_length; ++t) {
        // Run forward pass for this token via the opaque C-API
        hsru_llm_step(ctx, current_token, logits);
        
        // Apply Repetition Penalty (1.2)
        float rep_penalty = 1.2f;
        for (int i = 0; i < num_generated; ++i) {
            int past_id = generated_tokens[i];
            if (logits[past_id] > 0) {
                logits[past_id] /= rep_penalty;
            } else {
                logits[past_id] *= rep_penalty;
            }
        }

        // Top-K (50) and Temperature (0.7) Sampling
        int top_k = 50;
        float temperature = 0.7f;
        
        for (int v = 0; v < vocab_size; ++v) {
            token_probs[v].prob = logits[v] / temperature;
            token_probs[v].id = v;
        }
        
        // Sort descending by logit
        std::sort(token_probs, token_probs + vocab_size, [](const TokenProb& a, const TokenProb& b) {
            return a.prob > b.prob;
        });
        
        // Softmax over top-K
        float sum_probs = 0.0f;
        float max_logit = token_probs[0].prob; // For numerical stability
        for (int k = 0; k < top_k; ++k) {
            token_probs[k].prob = std::exp(token_probs[k].prob - max_logit);
            sum_probs += token_probs[k].prob;
        }
        
        // Sample
        float r = ((float)rand() / (float)RAND_MAX) * sum_probs;
        float accum = 0.0f;
        int best_token = token_probs[0].id;
        for (int k = 0; k < top_k; ++k) {
            accum += token_probs[k].prob;
            if (r <= accum) {
                best_token = token_probs[k].id;
                break;
            }
        }
        
        generated_tokens[num_generated++] = best_token;
        
        current_token = best_token;
        if (current_token == 50256) { // eos
            break; 
        }
        
        if (vocab[current_token]) std::cout << vocab[current_token];
        std::cout.flush();
    }
    
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end_time - start_time;
    
    std::cout << "\n\n[INFO] Generation Complete. Time: " << diff.count() << " s (" 
              << (num_generated + 1) / diff.count() << " tokens/sec)\n";

    for (int i = 0; i < vocab_size; ++i) {
        free(vocab[i]);
    }
    free(vocab);
    free(generated_tokens);
    free(token_probs);
    free(logits);
    hsru_llm_free_context(ctx);
    
    return 0;
}
