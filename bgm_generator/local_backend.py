"""stabilityai/stable-audio-open-1.0 をローカル(GPU)で実行して BGM を生成するバックエンド。

diffusers の StableAudioPipeline を利用する。初回実行時にモデル(数GB)が
Hugging Face からダウンロードされるため、ネットワークとディスク容量が必要。
GPU (CUDA / MPS) がない環境では非常に遅くなる、または動作しない場合がある。
"""
from __future__ import annotations

import numpy as np
import torch

_pipe = None
_MODEL_ID = "stabilityai/stable-audio-open-1.0"


def _load_pipeline(device: str):
    global _pipe
    if _pipe is None:
        from diffusers import StableAudioPipeline

        dtype = torch.float16 if device == "cuda" else torch.float32
        _pipe = StableAudioPipeline.from_pretrained(_MODEL_ID, torch_dtype=dtype)
        _pipe = _pipe.to(device)
    return _pipe


def generate_bgm(
    prompt: str,
    duration: float = 30.0,
    negative_prompt: str = "Low quality, distorted, noisy, harsh.",
    steps: int = 100,
    seed: int | None = None,
    device: str | None = None,
) -> tuple[np.ndarray, int]:
    """テキストプロンプトから BGM の波形データを生成する。

    Returns:
        (waveform, sample_rate) のタプル。waveform は soundfile.write にそのまま渡せる形状。
    """
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"

    pipe = _load_pipeline(device)

    generator = None
    if seed is not None:
        generator = torch.Generator(device).manual_seed(seed)

    result = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        audio_end_in_s=duration,
        num_waveforms_per_prompt=1,
        generator=generator,
    )
    audio = result.audios[0]
    waveform = audio.T.float().cpu().numpy()
    return waveform, pipe.vae.sampling_rate


def save_wav(path: str, waveform: np.ndarray, sample_rate: int) -> None:
    import soundfile as sf

    sf.write(path, waveform, sample_rate)
