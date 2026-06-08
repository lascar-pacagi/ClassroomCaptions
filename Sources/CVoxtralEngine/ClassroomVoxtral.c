#include "ClassroomVoxtral.h"
#include "Engine/voxtral.h"
#ifdef USE_METAL
#include "Engine/voxtral_metal.h"
#endif

#include <stdatomic.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define CCV_UPSTREAM_REVISION "134d366c24d20c64b614a3dcc8bda2a6922d077d"

struct ccv_model {
    vox_ctx_t *engine;
};

struct ccv_stream {
    ccv_model_t *model;
    vox_stream_t *engine;
    float *conversion_buffer;
    size_t conversion_capacity;
    const char *pending_text;
    uint64_t samples_fed;
    atomic_bool cancelled;
    int finished;
};

static void ccv_set_status(ccv_status_t *status, ccv_status_t value) {
    if (status) *status = value;
}

static void ccv_set_error(char *output, size_t capacity, const char *message) {
    if (!output || capacity == 0) return;
    snprintf(output, capacity, "%s", message ? message : "");
}

static int ccv_model_file_exists(const char *directory, const char *name) {
    char path[1024];
    int written = snprintf(path, sizeof(path), "%s/%s", directory, name);
    if (written < 0 || (size_t)written >= sizeof(path)) return 0;
    return access(path, R_OK) == 0;
}

ccv_stream_options_t ccv_stream_options_default(void) {
    ccv_stream_options_t options;
    options.delay_ms = 320;
    options.processing_interval_seconds = 1.0f;
    options.continuous = 1;
    options.max_decode_context_tokens = 2000;
    return options;
}

ccv_model_t *ccv_model_load(
    const char *model_directory,
    ccv_status_t *status,
    char *error_message,
    size_t error_message_capacity
) {
    ccv_set_status(status, CCV_STATUS_INVALID_ARGUMENT);
    ccv_set_error(error_message, error_message_capacity, "");
    if (!model_directory || model_directory[0] == '\0') {
        ccv_set_error(error_message, error_message_capacity, "Model directory is empty.");
        return NULL;
    }

    if (!ccv_model_file_exists(model_directory, "consolidated.safetensors")
        || !ccv_model_file_exists(model_directory, "tekken.json")
        || !ccv_model_file_exists(model_directory, "params.json")) {
        ccv_set_status(status, CCV_STATUS_MODEL_FILES_MISSING);
        ccv_set_error(
            error_message,
            error_message_capacity,
            "Model directory must contain consolidated.safetensors, tekken.json, and params.json."
        );
        return NULL;
    }

    ccv_model_t *model = calloc(1, sizeof(*model));
    if (!model) {
        ccv_set_status(status, CCV_STATUS_MODEL_LOAD_FAILED);
        ccv_set_error(error_message, error_message_capacity, "Unable to allocate model handle.");
        return NULL;
    }

#ifdef USE_METAL
    if (!vox_metal_init()) {
        free(model);
        ccv_set_status(status, CCV_STATUS_BACKEND_UNAVAILABLE);
        ccv_set_error(
            error_message,
            error_message_capacity,
            "Metal initialization failed; CPU fallback is disabled for live captions."
        );
        return NULL;
    }
#endif

    model->engine = vox_load(model_directory);
    if (!model->engine) {
#ifdef USE_METAL
        vox_metal_shutdown();
#endif
        free(model);
        ccv_set_status(status, CCV_STATUS_MODEL_LOAD_FAILED);
        ccv_set_error(error_message, error_message_capacity, "Voxtral model loading failed.");
        return NULL;
    }

    ccv_set_status(status, CCV_STATUS_OK);
    return model;
}

void ccv_model_free(ccv_model_t *model) {
    if (!model) return;
    vox_free(model->engine);
#ifdef USE_METAL
    vox_metal_shutdown();
#endif
    free(model);
}

ccv_stream_t *ccv_stream_create(
    ccv_model_t *model,
    ccv_stream_options_t options,
    ccv_status_t *status,
    char *error_message,
    size_t error_message_capacity
) {
    ccv_set_status(status, CCV_STATUS_INVALID_ARGUMENT);
    ccv_set_error(error_message, error_message_capacity, "");
    if (!model || !model->engine) {
        ccv_set_error(error_message, error_message_capacity, "Model handle is invalid.");
        return NULL;
    }

    ccv_stream_t *stream = calloc(1, sizeof(*stream));
    if (!stream) {
        ccv_set_status(status, CCV_STATUS_STREAM_CREATE_FAILED);
        ccv_set_error(error_message, error_message_capacity, "Unable to allocate stream handle.");
        return NULL;
    }

    vox_set_delay(model->engine, options.delay_ms);
    stream->engine = vox_stream_init(model->engine);
    if (!stream->engine) {
        free(stream);
        ccv_set_status(status, CCV_STATUS_STREAM_CREATE_FAILED);
        ccv_set_error(error_message, error_message_capacity, "Voxtral stream initialization failed.");
        return NULL;
    }

    stream->model = model;
    atomic_init(&stream->cancelled, 0);
    vox_set_processing_interval(stream->engine, options.processing_interval_seconds);
    vox_stream_set_continuous(stream->engine, options.continuous != 0);
    vox_stream_set_max_decode_context(
        stream->engine,
        options.max_decode_context_tokens
    );
    ccv_set_status(status, CCV_STATUS_OK);
    return stream;
}

ccv_status_t ccv_stream_feed_pcm16(
    ccv_stream_t *stream,
    const int16_t *samples,
    size_t sample_count
) {
    if (!stream || !samples || sample_count == 0) return CCV_STATUS_INVALID_ARGUMENT;
    if (atomic_load(&stream->cancelled)) return CCV_STATUS_CANCELLED;
    if (stream->finished) return CCV_STATUS_STREAM_FINISHED;

    if (sample_count > stream->conversion_capacity) {
        float *resized = realloc(stream->conversion_buffer, sample_count * sizeof(float));
        if (!resized) return CCV_STATUS_INFERENCE_FAILED;
        stream->conversion_buffer = resized;
        stream->conversion_capacity = sample_count;
    }

    for (size_t index = 0; index < sample_count; index++) {
        stream->conversion_buffer[index] = samples[index] / 32768.0f;
    }

    if (vox_stream_feed(
        stream->engine,
        stream->conversion_buffer,
        (int)sample_count
    ) != 0) {
        return CCV_STATUS_INFERENCE_FAILED;
    }
    stream->samples_fed += sample_count;
    return CCV_STATUS_OK;
}

ccv_status_t ccv_stream_flush(ccv_stream_t *stream) {
    if (!stream) return CCV_STATUS_INVALID_ARGUMENT;
    if (atomic_load(&stream->cancelled)) return CCV_STATUS_CANCELLED;
    if (stream->finished) return CCV_STATUS_STREAM_FINISHED;
    return vox_stream_flush(stream->engine) == 0
        ? CCV_STATUS_OK : CCV_STATUS_INFERENCE_FAILED;
}

ccv_status_t ccv_stream_finish(ccv_stream_t *stream) {
    if (!stream) return CCV_STATUS_INVALID_ARGUMENT;
    if (atomic_load(&stream->cancelled)) return CCV_STATUS_CANCELLED;
    if (stream->finished) return CCV_STATUS_STREAM_FINISHED;
    if (vox_stream_finish(stream->engine) != 0) {
        return CCV_STATUS_INFERENCE_FAILED;
    }
    stream->finished = 1;
    return CCV_STATUS_OK;
}

void ccv_stream_cancel(ccv_stream_t *stream) {
    if (stream) atomic_store(&stream->cancelled, 1);
}

ccv_status_t ccv_stream_read_text(
    ccv_stream_t *stream,
    char *output,
    size_t output_capacity,
    size_t *required_capacity
) {
    if (!stream) return CCV_STATUS_INVALID_ARGUMENT;

    if (!stream->pending_text) {
        const char *token = NULL;
        if (vox_stream_get(stream->engine, &token, 1) != 1 || !token) {
            if (required_capacity) *required_capacity = 0;
            return CCV_STATUS_NO_TEXT;
        }
        stream->pending_text = token;
    }

    size_t required = strlen(stream->pending_text) + 1;
    if (required_capacity) *required_capacity = required;
    if (!output || output_capacity < required) {
        return CCV_STATUS_BUFFER_TOO_SMALL;
    }

    memcpy(output, stream->pending_text, required);
    stream->pending_text = NULL;
    return CCV_STATUS_OK;
}

uint64_t ccv_stream_samples_fed(const ccv_stream_t *stream) {
    return stream ? stream->samples_fed : 0;
}

uint64_t ccv_stream_text_tokens_generated(const ccv_stream_t *stream) {
    return stream
        ? (uint64_t)vox_stream_text_token_count(stream->engine)
        : 0;
}

double ccv_stream_decoder_milliseconds(const ccv_stream_t *stream) {
    return stream
        ? vox_stream_decoder_milliseconds(stream->engine)
        : 0.0;
}

void ccv_stream_free(ccv_stream_t *stream) {
    if (!stream) return;
    vox_stream_free(stream->engine);
    free(stream->conversion_buffer);
    free(stream);
}

const char *ccv_status_description(ccv_status_t status) {
    switch (status) {
    case CCV_STATUS_OK: return "ok";
    case CCV_STATUS_NO_TEXT: return "no text available";
    case CCV_STATUS_BUFFER_TOO_SMALL: return "output buffer too small";
    case CCV_STATUS_INVALID_ARGUMENT: return "invalid argument";
    case CCV_STATUS_MODEL_FILES_MISSING: return "model files missing";
    case CCV_STATUS_MODEL_LOAD_FAILED: return "model load failed";
    case CCV_STATUS_STREAM_CREATE_FAILED: return "stream creation failed";
    case CCV_STATUS_STREAM_FINISHED: return "stream already finished";
    case CCV_STATUS_INFERENCE_FAILED: return "inference failed";
    case CCV_STATUS_CANCELLED: return "cancelled";
    case CCV_STATUS_BACKEND_UNAVAILABLE: return "inference backend unavailable";
    }
    return "unknown status";
}

const char *ccv_upstream_revision(void) {
    return CCV_UPSTREAM_REVISION;
}
