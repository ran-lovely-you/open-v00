"""AI BGM 生成 CLI。

使用例:
    python -m bgm_generator "calm lofi piano loop, 90 bpm" -o bgm.wav --backend local
    python -m bgm_generator "epic orchestral battle theme" -o bgm.mp3 --backend api
"""
from __future__ import annotations

import argparse
from pathlib import Path

from dotenv import load_dotenv


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="bgm_generator",
        description="Stable Audio を使ってテキストプロンプトから BGM を生成するツール",
    )
    parser.add_argument("prompt", help="生成したいBGMの説明 (英語推奨。例: 'peaceful ambient lofi, soft piano, 80 bpm')")
    parser.add_argument("-o", "--output", default="output.wav", help="出力ファイルパス")
    parser.add_argument("-d", "--duration", type=float, default=30.0, help="長さ(秒)。デフォルト30秒")
    parser.add_argument(
        "--backend",
        choices=["local", "api"],
        default="local",
        help="local: ローカルGPUでstable-audio-open-1.0を実行 / api: Stability AIのホスト型APIを使用",
    )
    parser.add_argument("--seed", type=int, default=None, help="乱数シード(再現性が欲しい場合)")
    parser.add_argument("--steps", type=int, default=100, help="推論ステップ数")
    return parser


def main(argv: list[str] | None = None) -> None:
    load_dotenv()
    args = build_parser().parse_args(argv)

    if args.backend == "local":
        from .local_backend import generate_bgm, save_wav

        print(f"[local] '{args.prompt}' を生成中... (steps={args.steps}, duration={args.duration}s)")
        waveform, sample_rate = generate_bgm(
            args.prompt, duration=args.duration, steps=args.steps, seed=args.seed
        )
        save_wav(args.output, waveform, sample_rate)
    else:
        from .api_backend import StabilityAudioClient

        print(f"[api] '{args.prompt}' を生成中...")
        client = StabilityAudioClient()
        audio_bytes = client.generate(
            args.prompt,
            duration=int(args.duration),
            seed=args.seed or 0,
            steps=args.steps,
        )
        Path(args.output).write_bytes(audio_bytes)

    print(f"生成完了: {args.output}")


if __name__ == "__main__":
    main()
