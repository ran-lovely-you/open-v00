# open-v00 — AI BGM Generator (Stable Audio)

Claude Code を使って開発した、Stability AI の **Stable Audio** でテキストプロンプトから
BGM(バックグラウンドミュージック)を自動生成するツールです。

- CLI と Web UI (Gradio) の両方を用意
- 2つの生成方式に対応
  - **local**: `stabilityai/stable-audio-open-1.0` をローカルGPUで実行(無料・オープンウェイト)
  - **api**: Stability AI のホスト型 REST API を利用(GPU不要・要APIキー・従量課金)

## もっと手軽に: index.html 版

Python環境を用意せず、個人のPCですぐ試したい場合は `index.html` を使ってください。
Stability AI API のみを呼び出す単一HTMLファイルで、ビルドやインストールは不要です。

1. `index.html` をブラウザで開く(ダブルクリックでOK。CORSでブロックされる場合は
   同じフォルダで `python -m http.server` を実行し `http://localhost:8000` から開く)
2. APIキーを入力(このブラウザの localStorage にのみ保存され、他へは送信されません)
3. プロンプトと長さを指定して「BGMを生成」

ローカルGPUによる無料生成(`stabilityai/stable-audio-open-1.0`)は使えず、
Stability AI のホスト型API(従量課金・要APIキー)のみに対応しています。
GPU環境がある場合は下記のPython版(`local` バックエンド)を使うと無料で生成できます。

## セットアップ (Python版)

```bash
python -m venv .venv
source .venv/bin/activate  # Windows は .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

`api` バックエンドを使う場合は、[platform.stability.ai](https://platform.stability.ai) で
APIキーを発行し、`.env` の `STABILITY_API_KEY` に設定してください。
`local` バックエンドのみを使う場合は `.env` の設定は不要です(初回実行時に
Hugging Face からモデル `stabilityai/stable-audio-open-1.0` が自動ダウンロードされます。
数GBの空き容量とGPUを推奨)。

## 使い方

### Web UI

```bash
python app.py
```

ブラウザで `http://127.0.0.1:7860` を開き、プロンプトと長さを指定して「BGMを生成」を押すだけです。

### CLI

```bash
# ローカルGPUで生成 (デフォルト)
python -m bgm_generator "peaceful ambient lofi background music, soft piano, 80 bpm" -o bgm.wav

# Stability AI API で生成
python -m bgm_generator "epic orchestral battle theme" -o bgm.mp3 --backend api --duration 60
```

主なオプション:

| オプション | 説明 |
|---|---|
| `-o, --output` | 出力ファイルパス |
| `-d, --duration` | 長さ(秒)。デフォルト30秒 |
| `--backend` | `local` または `api` |
| `--steps` | 推論ステップ数(多いほど高品質・低速)。デフォルト100 |
| `--seed` | 乱数シード。同じ値なら同じ結果を再現可能 |

## プロンプトのコツ

Stable Audio は英語プロンプトに最適化されています。ジャンル・楽器・テンポ(BPM)・雰囲気を
具体的に書くと安定します。

- `"lofi hip hop beat, mellow piano, vinyl crackle, 85 bpm, relaxing study background music"`
- `"dark ambient dungeon exploration music, low drones, subtle percussion, looping"`
- `"upbeat 8-bit chiptune, energetic, 140 bpm, video game shop theme"`

## 構成

```
app.py                    # Gradio Web UI
bgm_generator/
  cli.py                  # CLIエントリポイント
  local_backend.py        # diffusers StableAudioPipeline によるローカル生成
  api_backend.py          # Stability AI ホスト型APIクライアント
requirements.txt
.env.example
```

## 注意事項

- `local` バックエンドが使用する `stable-audio-open-1.0` は Stability AI Community License
  が適用されます。商用利用の可否・条件は必ず
  [ライセンス条項](https://huggingface.co/stabilityai/stable-audio-open-1.0) を確認してください。
- `api_backend.py` の Stability AI エンドポイント・パラメータは執筆時点の情報に基づいています。
  Stability AI 側の仕様変更に備え、実際に使う前に
  [公式APIドキュメント](https://platform.stability.ai/docs/api-reference) を確認し、
  必要であれば `.env` の `STABILITY_API_BASE` で上書きしてください。
- このリポジトリのコードはネットワーク制限のあるサンドボックス環境で作成されたため、
  実際のモデルダウンロード・生成の動作確認は行えていません。手元のGPU環境、または
  Stability AI APIキーを用意した環境で動作確認してください。
