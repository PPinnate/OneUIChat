# QwenWorkbench Roadmap

## MVP-0 (implemented)
- Scaffold, docs, registry, HF token handling, download manager, and model exploration checks.
- ChatGPT-style chatroom UI shell and local chat history stub endpoint.
- macOS one-click launcher (`QwenWorkbench.command`) with virtual environment setup.

## MVP-1
- ProcessManager with start/stop/status for worker subprocesses
- Proven unload via process termination and memory release telemetry

## MVP-2
- Chat endpoint + streaming with Qwen3-Next-80B-A3B-Instruct GGUF Q3 variants

## MVP-3
- Code endpoint + dedicated coding worker (Qwen3-Coder-Next)

## MVP-4
- ASR/TTS python workers + Speech tab integration

## MVP-5
- OCR/VLM worker with image + PDF rendering pipeline and document QA

## MVP-6
- Text-to-Image worker with Tongyi-MAI Z-Image-Turbo

## MVP-7 (Experimental)
- Wan2.1 T2V worker behind feature flag
