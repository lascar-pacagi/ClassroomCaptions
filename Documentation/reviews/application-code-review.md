# Application Code Review — Bugs, Security, Performance

Date: 2026-06-09. Reviewed by Claude (four focused passes: Swift correctness and
concurrency; network/Gemma security; C engine correctness; performance). Every
finding was verified against the source before inclusion; line numbers refer to
the working tree at review time. Severity is 1 (minor) to 5 (critical).

## Fix status (2026-06-10)

All bug and vulnerability findings below were fixed, built, and tested (69/69
tests pass, including new regression tests for the recognizeAll overlap crash,
the WAV header boundary, and the per-source ticket cap):

- **Fixed (Swift):** slowloris request timeout (10 s, `requestTimeout`);
  double-start race (`isStartingSession` held until listening/failure);
  recognizeAll overlap crash (longest-match-wins filter); shutdown on every
  termination path (`willTerminateNotification` observer); WebSocket audio
  ordering (synchronous send from the capture queue); stale correction-worker
  generation guard; accepted-question lifetime cap → sliding hourly window;
  app pending-question cap raised to a pure memory bound (500); provisional
  voice-command tracking keyed by action sequence instead of count; WAV header
  guard at `UInt32.max - 36`; lsof lookup moved off the main actor; per-source
  ticket cap (4); SSE slot pre-emption by a newer authenticated viewer.
- **Fixed (C engine):** WAV `sample_rate <= 0` rejection (both parsers); JSON
  trailing-backslash overreads (tokenizer parse_str/skip_value ×2, safetensors
  parse_string); `kv_cache_grow` zero-guard; safetensors bounds check by
  subtraction + `parse_int` overflow clamp; mel-context DFT-table leak; stdin
  ≥2 GiB chunk-size truncation; `get_merged_f16_3` cache key now includes the
  third pointer; encoder incremental forward batches at
  `VOX_ENC_INC_MAX_BATCH` so the fixed shared KV cache can never silently
  discard audio; `tok_embeddings` element count validated at load.
- **Not yet addressed (deliberately):** the real-time-callback allocation
  hardening (medium-risk audio change, needs manual listening tests), the
  broad unchecked-malloc cluster, systemic per-tensor shape validation beyond
  `tok_embeddings`, and plaintext HTTP (accepted design limitation).

## Performance fix status (2026-06-10)

Implemented and benchmarked against the same 10 s WAV on the development
machine (VoxtralBenchmark, release build):

| Metric | Before | After |
| --- | --- | --- |
| `model_load_seconds` (cold) | 4.50 | **0.68–0.70** (6.5×) |
| Peak RSS | 25.50 GB | **18.57 GB** (−6.9 GB) |
| `realtime_factor` | 0.2378 | 0.2375 (unchanged) |

- **GPU weight dedup:** merged QKV/w1w3 buffers are converted directly from
  bf16 with no permanent individual component caches; redundant decoder
  individual warmups removed; `vox_metal_memory_used` now counts merged
  buffers.
- **NEON + parallel bf16→f16** (`convert_bf16_to_f16`): 8 elements/iteration
  via f32 `vcvt` (round-to-nearest — at most 1 ulp different from the old
  truncating scalar, slightly more accurate), `dispatch_apply` across cores
  for large tensors, converting in place into the shared MTLBuffer.
- **Model retained across sessions** (`VoxtralEmbeddedService`): stop frees
  only the stream; the next start with the same model directory skips the
  load entirely. `releaseModel()` runs on app shutdown. The tokenizer is also
  cached on the model context instead of re-parsing tekken.json per stream.
  Measured with the new `VoxtralBenchmark --restart-test` mode (one model,
  two session cycles): restart stream-create 0.002 s, silence priming ~0.7 s,
  stop-side engine flush ~0.4 s — i.e. the engine cost of a stop/start cycle
  is ~1.1 s, dominated by the intentional 3.2 s-of-silence warm-up. App-side
  stop additionally waits (bounded) for pending Gemma corrections.
- **Decoder KV cache right-sized** in `ccv_stream_create` to the restart
  bound + 256 instead of the full 8192-position window (−~740 MB resident at
  the default context; grows on demand).
- **Swift hot path:** drainText emits one provisional + one metrics event per
  token burst instead of two events per token; the voice-command scanner
  tokenizes the caption text once across all five phrases (and guards before
  tokenizing in the potential-command path); meter/byte observable writes
  throttled to ~15 Hz; overlay/remote snapshot lines computed O(3) from the
  timeline tail instead of filtering the whole array; SSE `JSONEncoder`
  reused.
- **Deliberately skipped:** f16 encoder KV cache (−264 MB, but switches the
  live encoder numerics path — needs dedicated validation), conv-stem scratch
  reuse (~1–3 ms/s, riskiest code in the engine), mel DFT → vDSP (saves only
  ~3–6 ms CPU per second of audio; 400-point size is awkward for vDSP), and
  the per-token logits-copy skip (6.5 MB/s, requires a decoder ABI change).

## Top items, in order of recommended attention

1. **Slowloris lockout of the caption server (SEV 4, no credentials needed).**
   `LocalCaptionServer.swift:238,263`. Connections have no read/idle timeout and
   auth happens only after a complete request is parsed; 64 idle sockets (the
   accept cap) lock out the professor's phone and every student page for as long
   as the attacker keeps them open. Fix: per-connection timer at accept that
   cancels connections without a complete request within a few seconds.
2. **Double-start race during the microphone permission prompt (SEV 3).**
   `ClassroomAppModel.swift:614,365,691,736`. `.connected` clears
   `isStartingSession` before the session exists; while the first-run TCC
   microphone dialog is up, Start can be clicked again, reloading the model
   mid-flight and double-starting the archive. Fix: keep `isStartingSession`
   true until `markListening()` or failure.
3. **`recognizeAll` crash on overlapping spoken-command phrases (SEV 3).**
   `SpokenOverlayCommand.swift:110-113`. Overlapping matches (one phrase a
   prefix of another, or two commands configured identically — the settings UI
   prevents neither) produce ranges invalidated by earlier `removeSubrange`
   calls: String index out-of-bounds trap mid-lecture. Fix: skip matches that
   overlap the previously accepted match after sorting.
4. **Cmd-Q leaks the multi-GB Gemma server process (SEV 3).**
   `ClassroomCaptionsApp.swift:25-27`, `GemmaServerController.swift:63`.
   `shutdown()` is wired only to the menu-bar Quit button; quitting any other
   way leaves the ~10 GB `mlx_lm.server` child resident. Fix: app delegate
   `applicationWillTerminate` → `model.shutdown()`.
5. **Encoder shared-KV ceiling silently discards audio on Metal (SEV 3, engine).**
   `voxtral.c:245,819-822`, `voxtral_encoder.c:354-358,464-471`. Any single
   encoder pass with more than ~5.1 s of new audio cannot grow the fixed shared
   cache; the mel is dropped and every later chunk fails until a watchdog reset.
   The live app (1.0 s interval) is safe; `vox_transcribe*` and benchmark runs
   with long chunks/intervals return empty transcripts. Fix: process at most
   `enc_kv_cache_max − VOX_ENC_WINDOW` positions per pass in a loop.
6. **~5.3 GB of duplicated f16 weights on the GPU (performance, biggest win).**
   `voxtral_metal.m:183-214`, `voxtral.c:207-231`. Merged QKV/w1w3 buffers are
   built by first individually converting and *permanently caching* each
   component buffer; the default paths only ever read the merged ones. Decoder
   ~3.9 GB + encoder ~1.3 GB never read again. Converting directly into the
   merged buffer cuts weight residency ~14.1 → ~8.8 GB. (Also:
   `vox_metal_memory_used` does not count merged buffers, so the diagnostics
   under-report by the same amount.)
7. **Full model reload on every session start (performance).**
   `VoxtralEmbeddedService.swift:60,201-203`. Start pays mmap + scalar bf16→f16
   of ~4.4 B elements + ~10.5 GB of merges every session (likely 10–20 s of the
   "Loading Voxtral" wait). Keep the `ccv_model` alive across sessions and
   recreate only the stream; also NEON+parallelize `bf16_to_f16`
   (`voxtral_metal.m:79-93`) to cut conversion to ~1–2 s.

## Bugs — Swift application

- **WebSocket backend can reorder audio chunks (SEV 3).**
  `ClassroomAppModel.swift:720-733`. Per-chunk unstructured `Task`s have no FIFO
  guarantee; chunk N+1 can reach the socket before N → garbled remote
  transcription. Embedded path is safe (serial queue). Fix: enqueue
  synchronously from the capture queue.
- **Stale correction worker clobbers the new worker handle (SEV 2).**
  `ClassroomAppModel.swift:940`. A cancelled worker resuming later nils a newer
  worker's task handle → duplicate workers, queue-depth drift, stop can export
  with a segment stuck in `.correcting`. Fix: generation-token guard.
- **Question caps drop accepted questions / kill the feature (SEV 2).**
  `ClassroomAppModel.swift:1291`, `LocalCaptionServer.swift:642,657`. The app
  drops questions beyond 100 pending after the server already answered 202; and
  `acceptedQuestionCount` never decrements, so after 100 accepted submissions in
  a session every student gets 429 with no operator signal. Fix: communicate the
  pending-cap back as a non-success status; make the session cap a sliding
  window or surface it on the dashboard.
- **Provisional voice-command counter can fire the wrong command (SEV 2).**
  `ClassroomAppModel.swift:1118-1134`. Index-based "already handled" counting
  assumes hypothesis revisions are append-only; a revised hypothesis
  (`bleu`→`rouge`) leaves the corrected command unexecuted. Fix: key handled
  commands by match position, not count.
- **Real-time-thread allocations in the AUHAL callback (SEV 2 risk).**
  `MicrophoneCaptureService.swift:69-96,315-357`. Per-callback `AVAudioPCMBuffer`
  ×2, `Mutex`, `Data` copy, and `AVAudioConverter.convert` on the render thread.
  Works, but is a priority-inversion/dropout risk under memory pressure. Fix:
  preallocated buffers/ring + convert on `processingQueue`.
- **WAV header overflow at the 4 GB boundary (SEV 1).**
  `SessionArchiveService.swift:99` + `SessionExport.swift:16`. Guard permits
  `UInt32.max` but header math adds 36 in UInt32 → trap (~37 h of audio). Fix:
  guard `<= UInt32.max - 36`.
- **Synchronous `lsof` on the main actor (SEV 1).** `GemmaServerController.swift:72-98`
  stalls UI if `lsof` is slow. Run off-main / cache the pid.

## Bugs — C engine

- **SIGFPE on WAV with `sample_rate == 0` (SEV 3, malformed file).**
  `voxtral_audio.c:110-111`, duplicated `voxtral.c:1469-1470`. Reject
  `sample_rate <= 0`.
- **Heap overread in JSON parsers on trailing backslash (SEV 3, malformed file).**
  `voxtral_tokenizer.c:97-134,164,172`, `voxtral_safetensors.c:27-39`. A string
  ending `\` steps past the NUL and scans adjacent heap. Bail on `\0` after a
  backslash.
- **`kv_cache_grow` infinite loop when `kv_cache_max == 0` (SEV 2, OOM-gated).**
  `voxtral_decoder.c:218-219`. The encoder twin already guards this; mirror it.
- **Safetensors bounds check can wrap (SEV 2, malformed file).**
  `voxtral_safetensors.c:273-275` plus unvalidated `parse_int` magnitudes.
  Validate by subtraction.
- **Tensor shapes never validated against expected dims (SEV 2, systemic).**
  Loaders check numel-fits-data only; an undersized `tok_embeddings` gives OOB
  mmap reads (possible SIGBUS). Assert `numel == expected` per weight.
- **Unchecked malloc/realloc cluster (SEV 1-2 aggregate).** Hot sites:
  `stream_conv_stem` (~10 allocs), `vox_decoder_prefill`, `ensure_dec_buffers`,
  conv im2col, tokenizer tables, text accumulators (realloc losing pointer).
- **Minor:** DFT-table leak on a `vox_mel_ctx_init` failure path
  (`voxtral_audio.c:549-554`); `vox_transcribe_stdin` int-truncates ≥2 GiB chunk
  sizes (`voxtral.c:1437-1438`); latent `get_merged_f16_3` cache key ignores its
  third pointer (`voxtral_metal.m`) — aliasing if two merges ever share the
  first two pointers.
- **Contract notes:** `ccv_stream_cancel` does not synchronize with in-flight
  calls (safe today only because Swift serializes everything on one queue);
  one-stream-per-model and one-model-at-a-time are unenforced by the bridge.

## Security

The web surface is genuinely well built — verified clean: no XSS (textContent /
createElement only; hex-only token interpolation), no SSE injection (JSON
encoding escapes newlines), no response splitting, strict CSP, constant-time
token compare, loopback-locked Gemma endpoint, argv-array process launch (no
shell), no path traversal in archives, question text sanitized (Cc/Cf rejected)
and never parsed as Markdown, questions never reach Gemma. Remaining findings
are availability, not confidentiality/integrity:

1. Slowloris lockout (top item 1, SEV 4).
2. **Ticket-table exhaustion (SEV 3).** `LocalCaptionServer.swift:546-552`. No
   per-source limit and no rate limit on `POST /student-ticket`; one student can
   fill all 256 tickets → everyone else gets 503 for up to 4 h. Cap tickets per
   source.
3. **Single SSE slot can be seized and held (SEV 3).**
   `LocalCaptionServer.swift:681`. Whoever connects `/events` first holds it;
   no reclaim. Let a new authenticated stream pre-empt the old.
4. **100-question per-session kill-switch (SEV 2).** See bugs above.
5. **Plaintext HTTP (SEV 2, accepted design limitation, already in README).**
   Tokens/captions sniffable on hostile Wi-Fi; this enables 2-3 for a passive
   attacker. Mitigation is the documented trusted-network/hotspot guidance.
6. Hardening: combining-mark ("Zalgo") floods render garbled (cosmetic);
   `tokensMatch` length early-return leaks length (fixed-length tokens, moot).

## Performance — ranked opportunities

1. Eliminate duplicated f16 weights: **−5.3 GB GPU residency** (top item 6). S-M.
2. Keep the model loaded across sessions: **10–20 s → ~0 s session start** (top
   item 7). S-M.
3. Parallel/NEON bf16→f16 conversion: **~9–13 s → ~1–2 s of first load**. M.
4. Coalesce token events + tokenize-once command scan: `drainText` emits 2
   events/token; each provisional re-tokenizes the text 10× on the main actor
   (`SpokenOverlayCommand.swift:213-216,255-258`) — ~60–200 ms main-actor stall
   per second near the end of long utterances. **~50–100× less caption-path
   main-actor CPU.** S-M.
5. Right-size the decoder KV cache to `max_decode_context`: **−760 MB resident**
   (`voxtral.c:238` allocates 9216 positions; the app restarts at 2000). S.
6. f16 encoder KV cache (kernels already exist): **−264 MB**. M.
7. Persistent scratch for conv-stem/encoder feed (~10-15 MB malloc churn/s). S-M.
8. Small Swift churn: throttle 100 Hz level-meter mutations to ≤15 Hz; use
   `recentSegments(limit:)` instead of filtering the whole segments array per
   event; reuse one `JSONEncoder`; skip the 524 KB logits copy when `n_alt==1`.
9. Mel direct DFT → vDSP: only ~3–6 ms CPU per second of audio; 400-point size
   is awkward for vDSP FFT; battery polish only. Low priority.

Structural note: decode is weight-bandwidth-bound (~6.9 GB f16 read per token ≈
86 GB/s at 12.5 tok/s). The only big lever beyond the above is weight
quantization.

**Already well-optimized — do not touch:** the monolithic one-command-buffer
GPU steps (decoder token, encoder chunk, prefill) with zero-copy shared KV and
fp16 decoder cache; mmap'd bf16 weights with shape-keyed MPS op caching, pooled
activations, and load-time warmup (plus the 3.2 s silence pre-roll); the entire
incremental streaming design (tail buffers, compaction with position offsets —
nothing ever reprocesses old audio); the NEON fused bf16 matvec on the CPU
fallback path.
