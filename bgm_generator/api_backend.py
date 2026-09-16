"""Stability AI のホスト型 Stable Audio API を呼び出すバックエンド。

GPU を持たない環境でも BGM を生成できる。要 STABILITY_API_KEY。

注意: Stability AI の API エンドポイントやパラメータは変更されることがある。
利用前に https://platform.stability.ai/docs/api-reference の最新情報を必ず確認し、
必要であれば環境変数 STABILITY_API_BASE でエンドポイントを上書きすること。
"""
from __future__ import annotations

import os

import requests

DEFAULT_API_BASE = "https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio"


class StabilityAudioClient:
    def __init__(self, api_key: str | None = None, api_base: str | None = None):
        self.api_key = api_key or os.environ.get("STABILITY_API_KEY")
        if not self.api_key:
            raise RuntimeError(
                "STABILITY_API_KEY が設定されていません。.env に設定するか、"
                "環境変数として export してください。"
            )
        self.api_base = api_base or os.environ.get("STABILITY_API_BASE", DEFAULT_API_BASE)

    def generate(
        self,
        prompt: str,
        duration: int = 30,
        seed: int = 0,
        steps: int = 30,
        output_format: str = "mp3",
    ) -> bytes:
        """プロンプトから BGM を生成し、音声データ(bytes)を返す。"""
        response = requests.post(
            self.api_base,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Accept": "audio/*",
            },
            # Stability の v2beta API は multipart/form-data を要求するため、
            # ファイルを送らない場合でも files パラメータを指定して強制する。
            files={"none": ""},
            data={
                "prompt": prompt,
                "duration": duration,
                "seed": seed,
                "steps": steps,
                "output_format": output_format,
            },
            timeout=180,
        )

        if response.status_code != 200:
            raise RuntimeError(
                f"Stability AI API エラー (status={response.status_code}): {response.text}"
            )

        return response.content
