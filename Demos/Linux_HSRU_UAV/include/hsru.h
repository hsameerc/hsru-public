#ifndef HSRU_H
#define HSRU_H
#include <stdint.h>

#ifndef HSRU_API
#ifdef _WIN32
  #define HSRU_API __declspec(dllexport)
#else
  #define HSRU_API __attribute__((visibility("default")))
#endif
#endif

// External C-APIs for Python DLL and main.cpp
#ifdef __cplusplus
extern "C" {
#endif
    HSRU_API bool hsru_authenticate(const char* hardware_id);
    HSRU_API void* hsru_init_context(const char* weights_path, int num_layers, int hidden_size, int sensor_dim);
    HSRU_API void hsru_release_context(void* ctx);
    HSRU_API void hsru_release_context_fxp(void* ctx);
    HSRU_API void* hsru_init_context_fxp(const char* weights_path, int num_layers, int hidden_size, int sensor_dim);
    HSRU_API void hsru_step(void* ctx, const float* input, float* output);
    HSRU_API void hsru_step_fxp(void* ctx, const int32_t* input, int32_t* output);
    HSRU_API float hsru_get_sensor_std(int i);
    HSRU_API float hsru_compute_normalized_mse_fxp(const float* actual, const float* predicted, int sensor_dim);
#ifdef __cplusplus
}
#endif

#endif // HSRU_H
