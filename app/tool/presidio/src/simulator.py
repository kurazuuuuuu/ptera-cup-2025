import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sentence_transformers import SentenceTransformer

class BehaviorPredictor:
    def __init__(self, training_data_path):
        print("Training behavior prediction model...")
        self.df = pd.read_csv(training_data_path)
        self.features = ['weekday', 'hour', 'month', 'day', 'is_weekend']
        self.target = 'category'
        X = self.df[self.features]
        y = self.df[self.target]
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.model.fit(X, y)
        print(f"Model trained on {len(self.df)} records.")

    def predict(self, dt: datetime):
        input_data = pd.DataFrame([{
            'weekday': dt.weekday(),
            'hour': dt.hour,
            'month': dt.month,
            'day': dt.day,
            'is_weekend': 1 if dt.weekday() >= 5 else 0
        }])
        prediction = self.model.predict(input_data)[0]
        probs = self.model.predict_proba(input_data)[0]
        confidence = max(probs)
        return prediction, confidence

class MemorySearch:
    def __init__(self):
        print("Initializing vector search engine...")
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        self.memos = [
            "最近腰が痛いので無理な運動は避けたい",
            "駅前に新しいイタリアンレストランができたらしい。行ってみたい。",
            "プロジェクトAの進捗が遅れている。クライアントに謝罪が必要。",
            "田中さんは来週誕生日だ。",
            "新しいランニングシューズを買った。",
            "週末は映画を見に行きたい。",
            "最近野菜不足だからサラダを食べるようにする。",
            "部長との面談では来期の予算について話す必要がある。"
        ]
        self.embeddings = self.model.encode(self.memos)
        print(f"Indexed {len(self.memos)} memos.")

    def search(self, query: str, top_k: int = 2):
        query_vec = self.model.encode([query])
        similarities = np.dot(self.embeddings, query_vec.T).flatten()
        top_indices = np.argsort(similarities)[::-1][:top_k]
        results = []
        for idx in top_indices:
            results.append((self.memos[idx], similarities[idx]))
        return results

class LLMGenerator:
    def generate(self, dt: datetime, category: str, related_memos: list):
        print("\n--- LLM Generation Prompt ---")
        prompt = f"""
        日時: {dt}
        予測カテゴリ: {category}
        関連メモ:
        {chr(10).join([f'- {m}' for m, s in related_memos])}
        
        指示: 上記の情報を統合し、カレンダーに登録する予定タイトルを生成してください。
        """
        print(prompt)
        print("-----------------------------")
        
        if category == "Meal":
            if any("イタリアン" in m for m, _ in related_memos): return "駅前の新イタリアンでディナー"
            if any("野菜" in m for m, _ in related_memos): return "サラダ専門店でヘルシーランチ"
            return "ランチ"
        elif category == "Work":
            if any("プロジェクトA" in m for m, _ in related_memos): return "プロジェクトA 緊急対策会議"
            if any("部長" in m for m, _ in related_memos): return "部長と来期予算MTG"
            return "作業時間"
        elif category == "Health":
            if any("腰が痛い" in m for m, _ in related_memos): return "整形外科に行く (腰痛)"
            if any("シューズ" in m for m, _ in related_memos): return "新しい靴で試し走り"
            return "ジム"
        elif category == "Private":
            if any("映画" in m for m, _ in related_memos): return "映画鑑賞"
            return "自由時間"
        return f"{category}の予定"

def run_simulation(target_date_str: str, training_data_path: str):
    print(f"\n=== Simulation Start: {target_date_str} ===")
    target_dt = datetime.strptime(target_date_str, "%Y/%m/%d %H:%M")
    
    predictor = BehaviorPredictor(training_data_path)
    category, conf = predictor.predict(target_dt)
    print(f"Step 1 [Core ML]: Predicted '{category}' (Confidence: {conf:.2f})")
    
    search_query = f"{category} {target_dt.month}月"
    rag = MemorySearch()
    related_memos = rag.search(search_query)
    print(f"Step 2 [RAG]: Found {len(related_memos)} related memos.")
    for m, s in related_memos:
        print(f"  - [{s:.2f}] {m}")
        
    llm = LLMGenerator()
    event_title = llm.generate(target_dt, category, related_memos)
    print(f"\n>>> Final Output: '{event_title}'")
