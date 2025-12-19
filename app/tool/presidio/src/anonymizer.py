from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig
from presidio_analyzer.nlp_engine import NlpEngineProvider

# 設定: 日本語モデルを使用するための構成
NLP_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "ja", "model_name": "ja_core_news_lg"}],
}

def setup_engines():
    """PresidioのAnalyzerとAnonymizerを初期化する"""
    provider = NlpEngineProvider(nlp_configuration=NLP_CONFIG)
    nlp_engine = provider.create_engine()
    
    analyzer = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["ja"])
    anonymizer = AnonymizerEngine()
    return analyzer, anonymizer

def anonymize_text(text: str, analyzer: AnalyzerEngine, anonymizer: AnonymizerEngine) -> str:
    """テキスト内のPIIを検出して匿名化する"""
    if not isinstance(text, str) or not text:
        return ""
    
    # 解析 (日本語として解析)
    results = analyzer.analyze(text=text, language="ja")
    
    # 匿名化設定
    operators = {
        "PERSON": OperatorConfig("replace", {"new_value": "<PERSON>"}),
        "LOCATION": OperatorConfig("replace", {"new_value": "<LOCATION>"}),
        "GPE": OperatorConfig("replace", {"new_value": "<LOCATION>"}),
        "PHONE_NUMBER": OperatorConfig("replace", {"new_value": "<PHONE>"}),
        "EMAIL_ADDRESS": OperatorConfig("replace", {"new_value": "<EMAIL>"}),
        "URL": OperatorConfig("replace", {"new_value": "<URL>"}),
        "DATE_TIME": OperatorConfig("keep", {}),
    }
    
    anonymized_result = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators=operators
    )
    
    return anonymized_result.text
