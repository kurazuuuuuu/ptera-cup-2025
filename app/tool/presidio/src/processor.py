import pandas as pd
from .anonymizer import setup_engines, anonymize_text

def determine_category(subject: str) -> str:
    """件名からカテゴリを簡易的に判定する"""
    if not subject:
        return "Private"
    
    subject_lower = subject.lower()
    
    if any(k in subject_lower for k in ["ランチ", "ディナー", "食事", "飲み会", "ご飯"]):
        return "Meal"
    if any(k in subject_lower for k in ["ミーティング", "会議", "進捗", "資料", "連絡", "訪問", "面談"]):
        return "Work"
    if any(k in subject_lower for k in ["病院", "検診", "ジム", "トレーニング"]):
        return "Health"
    
    return "Private"

def process_dataframe_to_csv(df: pd.DataFrame, output_file: str):
    """DataFrameを受け取り、匿名化してフラットなCSVで出力する"""
    
    analyzer, anonymizer = setup_engines()
    
    # カラム名の正規化
    df.columns = [c.lower().strip() for c in df.columns]
    
    # カラム検索
    subject_col = next((c for c in df.columns if 'subject' in c or '件名' in c or 'title' in c), None)
    desc_col = next((c for c in df.columns if 'description' in c or '説明' in c or 'notes' in c), None)
    loc_col = next((c for c in df.columns if 'location' in c or '場所' in c), None)
    start_col = next((c for c in df.columns if 'start' in c and ('date' in c or 'time' in c) or '開始' in c), None)
    end_col = next((c for c in df.columns if 'end' in c and ('date' in c or 'time' in c) or '終了' in c), None)

    if not subject_col or not start_col:
        print("Error: Could not identify 'Subject' or 'Start Date' columns.")
        return

    print(f"Processing {len(df)} records for anonymization and feature extraction...")
    
    processed_records = []
    
    for index, row in df.iterrows():
        original_subject = str(row[subject_col]) if pd.notna(row[subject_col]) else ""
        description = str(row[desc_col]) if desc_col and pd.notna(row[desc_col]) else ""
        location = str(row[loc_col]) if loc_col and pd.notna(row[loc_col]) else ""
        
        category = determine_category(original_subject)
        anon_subject = anonymize_text(original_subject, analyzer, anonymizer)
        anon_description = anonymize_text(description, analyzer, anonymizer)
        anon_location = "<LOCATION>" if location.strip() else ""

        try:
            start_str = str(row[start_col])
            if 'time' not in start_col.lower():
                start_time_col = next((c for c in df.columns if 'start' in c and 'time' in c), None)
                if start_time_col and pd.notna(row[start_time_col]):
                    start_str += f" {row[start_time_col]}"
            
            start_dt = pd.to_datetime(start_str)

            end_str = str(row[end_col]) if end_col and pd.notna(row[end_col]) else str(start_dt)
            if end_col and 'time' not in end_col.lower():
                end_time_col = next((c for c in df.columns if 'end' in c and 'time' in c), None)
                if end_time_col and pd.notna(row[end_time_col]):
                    end_str += f" {row[end_time_col]}"
            
            end_dt = pd.to_datetime(end_str) if end_col else start_dt

            duration = (end_dt - start_dt).total_seconds() / 60
            
            weekday = start_dt.weekday()
            hour = start_dt.hour
            month = start_dt.month
            day = start_dt.day
            is_weekend = True if weekday >= 5 else False

        except Exception:
            start_dt = None
            end_dt = None
            duration = 0
            weekday = None
            hour = None
            month = None
            day = None
            is_weekend = False

        record = {
            "start": start_dt.isoformat() if start_dt else None,
            "end": end_dt.isoformat() if end_dt else None,
            "duration_minutes": duration,
            "weekday": weekday,
            "hour": hour,
            "month": month,
            "day": day,
            "is_weekend": 1 if is_weekend else 0,
            "category": category,
            "original_subject_length": len(original_subject),
            "subject": anon_subject,
            "description": anon_description,
            "location": anon_location
        }
        processed_records.append(record)

    output_df = pd.DataFrame(processed_records)
    print(f"Writing to {output_file}...")
    output_df.to_csv(output_file, index=False, encoding='utf-8')
    print("Done.")
