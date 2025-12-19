# AI Architecture & Implementation Strategy

## 1. Overview
本プロジェクトでは、**「プライバシー保護」**と**「高度なパーソナライゼーション」**を両立するため、オンデバイス学習（Core ML）と生成AI（Local LLM）を組み合わせた**ハイブリッドAIアーキテクチャ**を採用します。
ユーザーの行動パターン学習には軽量かつ高速な機械学習モデルを使用し、具体的なテキスト生成には文脈理解に優れたLLMを使用することで、高速なレスポンスと人間味のある提案を実現します。

## 2. System Architecture

```mermaid
graph TD
    User[User / Calendar Input] -->|Raw Data| AppLogic
    
    subgraph "Python Tool (Pre-development)"
        Faker[Faker Data Generator] -->|Google Calendar CSV| Presidio[Presidio Anonymizer]
        Presidio -->|Anonymized CSV| CreateML[Create ML Training]
    end
    
    CreateML -->|Core ML Model| AppLogic[iOS App Logic]
    
    subgraph "iOS On-Device Processing"
        AppLogic -->|Date & Time Features| CoreML[Core ML Model]
        CoreML -->|Predicted Category| RAG[Vector Search (RAG)]
        AppLogic -->|User Memos| VectorDB[Vector Database]
        VectorDB -->|Relevant Context| RAG
        RAG -->|Prompt Context| LocalLLM[Local LLM]
        LocalLLM -->|Generated Event| Calendar[iOS Calendar]
        
        Calendar -->|New Event Data| Updatable[Core ML Update Task]
        Updatable -->|Re-train| CoreML
    end
```

## 3. Key Components

### 3.1. Preprocessing & Base Model (Python Tool)
アプリ出荷前のベースモデルを作成するためのパイプライン。
*   **Data Generation**: `Faker` を使用し、Googleカレンダー形式のリアルなダミーデータを生成。
*   **Anonymization**: `Microsoft Presidio` により、学習データ内のPII（個人情報）を匿名化。
*   **Feature Engineering**: 日時情報から特徴量（`month`, `day`, `weekday`, `hour`, `is_weekend`）と正解ラベル（`category`）を抽出。
*   **Output**: Create ML (Tabular Classification) 用のCSVを出力。

### 3.2. Prediction Engine (Core ML)
ユーザーの行動傾向を瞬時に判断する軽量モデル。
*   **Model Type**: Tabular Classification (k-Nearest Neighbors 推奨)
*   **Input**: `month`, `day`, `weekday`, `hour`, `is_weekend`
*   **Output**: 行動カテゴリ (`Work`, `Meal`, `Health`, `Private` 等)
*   **Updatable**: ユーザーが実際に予定を追加するたびにオンデバイスで学習し、個人の癖（例: 月曜朝は必ずジムに行く）に適応する。

### 3.3. Semantic Memory (Vector Search / RAG)
LLMに「ユーザーの文脈」を与えるための記憶システム。
*   **Embedding**: ユーザーのメモや過去の予定をベクトル化して保存。
*   **Retrieval**: Core MLが予測したカテゴリ（例: `Health`）や日時に関連するキーワードで検索し、関連性の高いメモ（例: 「最近腰が痛い」）を抽出する。

### 3.4. Generative Engine (Local LLM)
最終的な出力を行う生成モデル。
*   **Role**: 文脈の統合と自然言語生成。
*   **Prompting**:
    *   **Context**: Core MLの予測カテゴリ + ベクトル検索で得たメモ
    *   **Constraint**: 日時指定（例: 2025/12/25 19:00）
    *   **Task**: 「上記を踏まえて、自然な予定タイトルを1つ生成せよ」

## 4. User Experience Flow

**シナリオ: ユーザーが「予定追加」ボタンを押し、日付のみを指定した場合**

1.  **Input**: ユーザーが `2025/12/25 19:00` を指定。
2.  **Feature Extraction**: アプリが日時から特徴量を抽出。
    *   `month: 12`, `day: 25`, `weekday: 3 (Thu)`, `hour: 19`, `is_weekend: False`
3.  **Prediction (Core ML)**: モデルが特徴量からカテゴリを予測。
    *   結果: **`Meal`** (クリスマス・ディナーの時間帯傾向)
4.  **Retrieval (RAG)**: `Meal` や `12月` に関連するメモを検索。
    *   Hit: "駅前のイタリアンが気になる", "〇〇さんとご飯行きたい"
5.  **Generation (LLM)**: 情報を統合して予定を生成。
    *   生成結果: **「〇〇さんと駅前イタリアンでディナー」**
6.  **Action**: カレンダーに予定が自動登録される。

## 5. Privacy & Security
*   **Local Processing**: 学習、推論、ベクトル検索、生成のすべてのプロセスがオンデバイス（ローカル）で完結する。サーバーへのデータ送信は一切行わない。
*   **Anonymization**: 開発時の学習データ作成においても `Presidio` を使用し、個人情報が含まれない状態（`<PERSON>` 等に置換済み）でベースモデルを作成する。
