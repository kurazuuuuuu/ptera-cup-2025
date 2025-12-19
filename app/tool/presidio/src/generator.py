import pandas as pd
import random
from faker import Faker

def generate_dummy_data(count: int = 500) -> pd.DataFrame:
    """生活リズムに基づいたリアルなダミーデータを生成する"""
    print(f"Generating {count} realistic dummy records (Google Calendar Format)...")
    fake = Faker('ja_JP')
    data = []

    # カテゴリごとのテンプレート
    templates = {
        "Meal": ["{name}さんとランチ", "{name}とディナー", "食事会", "ランチミーティング", "飲み会"],
        "Work": ["{name}とミーティング", "{company}への訪問", "定例会議", "{project}進捗確認", "資料作成: {project}", "{name}に連絡"],
        "Health": ["病院へ行く", "ジムでトレーニング", "内科検診", "ジョギング"],
        "Private": ["買い物: {place}", "美容院", "映画鑑賞", "読書", "家事"]
    }

    for _ in range(count):
        # 1. まず日時をランダムに生成
        start_dt = fake.date_time_between(start_date='-1y', end_date='+1y')
        weekday = start_dt.weekday()
        hour = start_dt.hour
        is_weekend = weekday >= 5

        # 2. 時間帯と曜日から「もっともらしい」カテゴリを選択
        if 9 <= hour <= 17 and not is_weekend:
            category = random.choices(["Work", "Meal", "Private"], weights=[0.8, 0.1, 0.1])[0]
        elif (11 <= hour <= 13) or (18 <= hour <= 20):
            category = random.choices(["Meal", "Work", "Private"], weights=[0.7, 0.1, 0.2])[0]
        elif (hour <= 8 or hour >= 21) or is_weekend:
            category = random.choices(["Private", "Health", "Meal"], weights=[0.6, 0.3, 0.1])[0]
        else:
            category = random.choice(["Work", "Meal", "Health", "Private"])

        # 3. カテゴリに応じたテキスト生成
        subj_tmpl = random.choice(templates[category])
        
        name = fake.name()
        company = fake.company()
        address = fake.address()
        phone = fake.phone_number()
        email = fake.email()
        url = fake.url()
        place = fake.city()
        project = fake.word().upper() + "プロジェクト" if hasattr(fake, 'word') else "次世代プロジェクト"

        subject = subj_tmpl.format(name=name, company=company, place=place, project=project)
        
        description = random.choice([
            "場所は{address}です。", "連絡先は{phone}です。", "詳細は {url} を参照。", "特になし。"
        ]).format(address=address, phone=phone, url=url)
        
        location = address if random.random() > 0.3 else fake.company()
        duration = random.choice([30, 60, 90, 120])
        end_dt = start_dt + pd.Timedelta(minutes=duration)

        data.append({
            "Subject": subject,
            "Start Date": start_dt.strftime('%Y-%m-%d'),
            "Start Time": start_dt.strftime('%H:%M'),
            "End Date": end_dt.strftime('%Y-%m-%d'),
            "End Time": end_dt.strftime('%H:%M'),
            "All Day Event": "False",
            "Description": description,
            "Location": location,
            "Private": "False"
        })

    columns = ["Subject", "Start Date", "Start Time", "End Date", "End Time", "All Day Event", "Description", "Location", "Private"]
    return pd.DataFrame(data, columns=columns)