/* hsru_codec.h  HSRUEcodec edge binary  (format version 2)
 *
 * Incompatible with LLM binary (format version 1).
 * Magic 0x48535255 + version field identify the format at load time.
 *
 * Load codec_manifest.json to get exact byte offset and shape of every
 * tensor, then fread or mmap into the C++ codec engine structs.
 */
#ifndef HSRU_CODEC_H
#define HSRU_CODEC_H
#include <stdint.h>

#define HSRU_CODEC_MAGIC   0x48535255u  /* "HSRU" */
#define HSRU_CODEC_VERSION 2

typedef struct {
    int32_t magic;           /* 0x48535255 */
    int32_t version;         /* 2 */
    int32_t dim;             /* latent dimension */
    int32_t codebook_size;   /* codes per RVQ level */
    int32_t num_quantizers;  /* RVQ levels */
    int32_t num_blocks;      /* HSRU blocks each side */
    int32_t k_dims;          /* thermometer thresholds */
    int32_t codebook_dim;    /* projected codebook dim */
    int32_t sample_rate;     /* e.g. 24000 */
    int32_t downsample;      /* total stride e.g. 320 */
    int32_t fxp;             /* 0=fp32  1=int8 */
    int32_t reserved;
} HSRUCodecHeader;

/* Per-block MemoryLayer weights (written in this exact order) */
typedef struct {
    float* norm1_weight;      /* [dim] */
    float* norm1_bias;        /* [dim] */
    float* w_leak_weight;     /* [dim x dim] */
    float* w_leak_bias;       /* [dim] */
    float* w_shunt_weight;    /* [dim x dim] */
    float* w_shunt_bias;      /* [dim] */
    float* linear_in_weight;  /* [dim x dim] */
    float* linear_in_bias;    /* [dim] */
    float* w_dend_in_weight;  /* [dim x dim] */
    float* w_dend_in_bias;    /* [dim] */
    float* w_dend_decay_weight;/* [dim x dim] */
    float* w_dend_decay_bias; /* [dim] */
    float* w_dend_out;        /* [dim] */
    float* dendrite_thresh;   /* [split_idx x k_dims] softplus pre-applied */
    float* target_rate;       /* [1] */
    float* threshold;         /* [split_idx x k_dims]  softplus pre-applied */
    float* w_v;               /* [dim] */
    float* w_d;               /* [split_idx x k_dims] */
    float* bias;              /* [dim] */
} HSRUCodecMemWeights;

/* Per-block LogicLayer weights */
typedef struct {
    float* norm2_weight;      /* [dim] */
    float* norm2_bias;        /* [dim] */
    float* w_gate_weight;     /* [logic_dim x dim] */
    float* w_gate_bias;       /* [logic_dim] */
    float* w_value_weight;    /* [logic_dim x dim] */
    float* w_value_bias;      /* [logic_dim] */
    float* w_out_weight;      /* [dim x logic_dim] */
    float* w_out_bias;        /* [dim] */
    float* out_norm_weight;   /* [dim] */
    float* out_norm_bias;     /* [dim] */
    float* mem_scale;         /* [dim] */
} HSRUCodecLogicWeights;

#ifdef __cplusplus
extern "C" {
#endif

void* hsru_codec_init_context(const char* weights_path);
void hsru_codec_encode(void* ctx, const float* audio, int num_samples, int* out_codes);
void hsru_codec_decode(void* ctx, const int* codes, int num_frames, float* out_audio);
void hsru_codec_free_context(void* ctx);

void* hsru_codec_create_state(void* ctx);
void hsru_codec_encode_stream(void* ctx, void* state, const float* audio, int num_samples, int* out_codes);
void hsru_codec_decode_stream(void* ctx, void* state, const int* codes, int num_frames, float* out_audio);
void hsru_codec_free_state(void* state);

#ifdef __cplusplus
}
#endif

#endif /* HSRU_CODEC_H */
