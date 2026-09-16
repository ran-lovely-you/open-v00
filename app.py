"""AI BGM Generator の Gradio Web UI。

起動:
    python app.py

ブラウザで http://127.0.0.1:7860 を開いて使用する。
"""
from __future__ import annotations

import gradio as gr
from dotenv import load_dotenv

load_dotenv()

BACKEND_LOCAL = "ローカル (stable-audio-open-1.0 / GPU推奨)"
BACKEND_API = "Stability AI API (要APIキー)"


def generate(prompt, duration, backend, steps, seed):
    if not prompt or not prompt.strip():
        raise gr.Error("プロンプトを入力してください。")

    seed_value = int(seed) if seed not in (None, "") else None

    if backend == BACKEND_LOCAL:
        from bgm_generator.local_backend import generate_bgm, save_wav

        waveform, sample_rate = generate_bgm(
            prompt, duration=float(duration), steps=int(steps), seed=seed_value
        )
        out_path = "output.wav"
        save_wav(out_path, waveform, sample_rate)
    else:
        from bgm_generator.api_backend import StabilityAudioClient

        client = StabilityAudioClient()
        audio_bytes = client.generate(
            prompt,
            duration=int(duration),
            seed=seed_value or 0,
            steps=int(steps),
        )
        out_path = "output.mp3"
        with open(out_path, "wb") as f:
            f.write(audio_bytes)

    return out_path


with gr.Blocks(title="AI BGM Generator (Stable Audio)") as demo:
    gr.Markdown(
        "# 🎵 AI BGM Generator\n"
        "Stable Audio を使ってテキストプロンプトから BGM を自動生成します。"
    )
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(
                label="プロンプト (英語推奨)",
                placeholder="例: peaceful ambient lofi background music, soft piano, 80 bpm, loopable",
                lines=3,
            )
            duration = gr.Slider(5, 180, value=30, step=1, label="長さ (秒)")
            backend = gr.Radio(
                [BACKEND_LOCAL, BACKEND_API], value=BACKEND_LOCAL, label="生成方式"
            )
            steps = gr.Slider(10, 200, value=100, step=1, label="ステップ数 (多いほど高品質・低速)")
            seed = gr.Number(label="シード (空欄でランダム)", value=None)
            btn = gr.Button("BGMを生成", variant="primary")
        with gr.Column():
            audio_out = gr.Audio(label="生成結果", type="filepath")

    btn.click(generate, inputs=[prompt, duration, backend, steps, seed], outputs=audio_out)

if __name__ == "__main__":
    demo.launch()
