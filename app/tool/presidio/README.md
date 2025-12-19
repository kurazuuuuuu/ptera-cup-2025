# Calendar Data Anonymizer for LLM/Create ML Training

個人のカレンダーデータ（CSV）からPII（個人識別情報）を検出し、匿名化して、Apple Create ML や LLM での学習に適した構造化データセット（CSV形式）を生成するツールです。

## 機能

- **PII検出と匿名化**: Microsoft Presidio と spaCy (日本語モデル `ja_core_news_lg`) を使用し、人名、電話番号、メールアドレス、URL、場所などを自動的に検出し、タグ（`<PERSON>`, `<LOCATION>`など）に置換します。
- **場所情報の保護**: カレンダーの「場所」フィールドは、プライバシー保護のため一律で `<LOCATION>` に置換されます。
- **Create ML対応**: 学習に使用しやすいフラットなCSV形式で出力します。

## 必要な環境

- Python 3.12+
- `uv` (推奨パッケージマネージャー)

## インストール

```bash
# 依存関係のインストール
uv sync

# spaCy日本語モデルのダウンロード
uv pip install https://github.com/explosion/spacy-models/releases/download/ja_core_news_lg-3.8.0/ja_core_news_lg-3.8.0-py3-none-any.whl
```

## 使い方

```bash
uv run main.py --input <入力CSVファイルパス> --output <出力CSVファイルパス>
```

例:
```bash
uv run main.py --input my_calendar.csv --output dataset.csv
```

### ダミーデータの生成
入力ファイルを指定しない場合、自動的にダミーデータが生成され、`generated/` ディレクトリ内に保存されます。

```bash
# 500件のダミーデータを生成して匿名化 (デフォルト)
# 生成されたファイルは generated/YYYYMMDD_HHMMSS_generated.csv として保存されます
uv run main.py

# 件数を指定する場合
uv run main.py --dummy-count 1000

# 出力先を明示的に指定する場合
uv run main.py --output custom_dataset.csv
```

## 入力CSVフォーマット
以下のヘッダーを持つ一般的なカレンダーエクスポート形式（Google Calendar, Outlook等）に対応しています。
- Subject (件名)
- Start Date (開始日)
- Start Time (開始時刻)
- End Date (終了日)
- End Time (終了時刻)
- Description (説明)
- Location (場所)

## 出力フォーマット (CSV)

以下のカラムを持つCSVが出力されます。

| カラム名 | 説明 | 例 |
| --- | --- | --- |
| start | 開始日時 (ISO8601) | 2025-12-14T02:56:00 |
| end | 終了日時 (ISO8601) | 2025-12-14T03:26:00 |
| duration_minutes | 所要時間(分) | 30.0 |
| weekday | 曜日 (0=月曜, 6=日曜) | 0 |
| hour | 開始時刻 (時) | 14 |
| month | 月 | 12 |
| day | 日 | 14 |
| is_weekend | 週末フラグ | True |
| category | 行動カテゴリ (Work, Meal等) | Work |
| original_subject_length | 元の件名の文字数 | 10 |
| subject | 匿名化された件名 | `<PERSON>`へ連絡する |
| description | 匿名化された説明 | 事前に `<EMAIL>` に連絡を入れておくこと。 |
| location | 匿名化された場所 | `<LOCATION>` |