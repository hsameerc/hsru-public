#ifndef HSRU_LLM_H
#define HSRU_LLM_H

#if defined(_MSC_VER)
    // Windows DLL export/import
    #ifndef HSRU_API
        #ifdef HSRU_EXPORTS
            #define HSRU_API __declspec(dllexport)
        #else
            #define HSRU_API __declspec(dllimport)
        #endif
    #endif
#else
    // Linux/macOS shared library export
    #ifndef HSRU_API
        #define HSRU_API __attribute__((visibility("default")))
    #endif
#endif

#ifdef __cplusplus
extern "C" {
#endif

// Opaque Context API for HSRU LLM
// Loads weights and allocates internal state arrays
HSRU_API void* hsru_llm_init_context(const char* weights_path);

// Performs a forward pass on a single token, returning the logits array
HSRU_API void hsru_llm_step(void* ctx, int current_token, float* out_logits);

// Returns the vocab size for the loaded context
HSRU_API int hsru_llm_get_vocab_size(void* ctx);

// Frees the context and all allocated memory
HSRU_API void hsru_llm_free_context(void* ctx);

// Saves the current biological memory and logic states to a binary file
HSRU_API int hsru_save_state(void* ctx, const char* filepath);

// Loads the biological memory and logic states from a binary file
HSRU_API int hsru_load_state(void* ctx, const char* filepath);


#ifdef __cplusplus
}
#endif

#endif
