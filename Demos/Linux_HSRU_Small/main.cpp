#include <iostream>
#include <string>
#include <vector>
#include "hsru_llm.h"

int main() {
    std::cout << "Loading HSRU Edge Model..." << std::endl;
    auto* ctx = hsru_llm_init_context("models/story_weights.bin");
    if (!ctx) {
        std::cerr << "Failed to load models/story_weights.bin! Make sure it is in the same directory." << std::endl;
        return 1;
    }
    
    std::cout << "Model Loaded! Type your message (type 'quit' to exit)." << std::endl;
    std::cout << "==========================================================" << std::endl;
    
    std::string user_input;
    while (true) {
        std::cout << "\nUser> ";
        if (!std::getline(std::cin, user_input)) break;
        if (user_input == "quit" || user_input == "exit") break;
        
        // Note: For a fully featured zero-dependency loop, you would load the JSON tokenizer here, 
        // tokenize `user_input`, feed the tokens to hsru_llm_step, and decode the logits.
        // This requires a simple C++ BPE tokenizer (e.g. minBPE or huggingface tokenizers cpp wrapper).
        std::cout << "Assistant> (C++ Inference logic will execute here...)\n";
    }
    
    hsru_llm_free_context(ctx);
    return 0;
}
