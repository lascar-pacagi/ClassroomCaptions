#ifndef CLASSROOM_VOXTRAL_H
#define CLASSROOM_VOXTRAL_H

#include <stddef.h>
#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct ccv_model ccv_model_t;
typedef struct ccv_stream ccv_stream_t;

typedef enum {
    CCV_STATUS_OK = 0,
    CCV_STATUS_NO_TEXT = 1,
    CCV_STATUS_BUFFER_TOO_SMALL = 2,
    CCV_STATUS_INVALID_ARGUMENT = -1,
    CCV_STATUS_MODEL_FILES_MISSING = -2,
    CCV_STATUS_MODEL_LOAD_FAILED = -3,
    CCV_STATUS_STREAM_CREATE_FAILED = -4,
    CCV_STATUS_STREAM_FINISHED = -5,
    CCV_STATUS_INFERENCE_FAILED = -6,
    CCV_STATUS_CANCELLED = -7,
    CCV_STATUS_BACKEND_UNAVAILABLE = -8
} ccv_status_t;

typedef struct {
    int delay_ms;
    float processing_interval_seconds;
    int continuous;
    int max_decode_context_tokens;
} ccv_stream_options_t;

ccv_stream_options_t ccv_stream_options_default(void);

ccv_model_t *ccv_model_load(
    const char *model_directory,
    ccv_status_t *status,
    char *error_message,
    size_t error_message_capacity
);

void ccv_model_free(ccv_model_t *model);

ccv_stream_t *ccv_stream_create(
    ccv_model_t *model,
    ccv_stream_options_t options,
    ccv_status_t *status,
    char *error_message,
    size_t error_message_capacity
);

ccv_status_t ccv_stream_feed_pcm16(
    ccv_stream_t *stream,
    const int16_t *samples,
    size_t sample_count
);

ccv_status_t ccv_stream_flush(ccv_stream_t *stream);
ccv_status_t ccv_stream_finish(ccv_stream_t *stream);
void ccv_stream_cancel(ccv_stream_t *stream);

ccv_status_t ccv_stream_read_text(
    ccv_stream_t *stream,
    char *output,
    size_t output_capacity,
    size_t *required_capacity
);

uint64_t ccv_stream_samples_fed(const ccv_stream_t *stream);
uint64_t ccv_stream_text_tokens_generated(const ccv_stream_t *stream);
double ccv_stream_decoder_milliseconds(const ccv_stream_t *stream);
void ccv_stream_free(ccv_stream_t *stream);

const char *ccv_status_description(ccv_status_t status);
const char *ccv_upstream_revision(void);

#ifdef __cplusplus
}
#endif

#endif
