# Upstream

Project: `antirez/voxtral.c`

Repository: https://github.com/antirez/voxtral.c

Pinned revision: `134d366c24d20c64b614a3dcc8bda2a6922d077d`

Imported: 2026-06-07

The source is maintained locally under `Sources/CVoxtralEngine/Engine`. The original
MIT license is retained in this directory.

Imported inference files:

- core model and streaming implementation;
- audio preprocessing;
- encoder, adapter, and decoder;
- tokenizer and safetensors reader;
- CPU kernels;
- Metal/MPS backend;
- generated Metal shader source.

Not imported:

- command-line program;
- microphone capture;
- samples and benchmarks;
- model download script;
- Python reference implementation.

Local modifications are documented in
`Documentation/voxtral-engine-internals.md`.
