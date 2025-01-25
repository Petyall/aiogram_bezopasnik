import pandas as pd

from joblib import load
from utils.url_classification import get_metrics
from utils.url_visualization import generate_html_report


prediction_model = load('./model/random_forest_model.pkl')

async def url_prediction(url: str):
    url_metric = await get_metrics(url)

    if not url_metric:
        return "⚠️Не удалось получить метрики для указанной ссылки⚠️"

    metrics = {
        key: url_metric[key] for key in [
            'length_url', 'length_hostname', 'is_ip', 'dots_qty', 'hyphens_qty', 'at_qty',
            'is_www', 'is_https', 'is_tld', 'suspicious_subdomains', 'subdomains_qty',
            'is_short_url', 'path_extension', 'has_redirection', 'suspicious_top_level_domain',
            'qty_hyperlinks', 'proportion_extHyperlinks', 'is_login_form', 'is_external_favicon',
            'iframe', 'is_empty_title', 'whois_registered_domain', 'domain_age'
        ]
    }

    df_metrics = pd.DataFrame([metrics])

    prediction_model = load('./model/random_forest_model.pkl')
    prediction = prediction_model.predict(df_metrics.values)[0]

    report_type = "phishing" if prediction == 1 else "legitimate"
    file_name = await generate_html_report(url, metrics, report_type)

    if prediction == 1:
        return "❌Осторожно, ссылка может быть опасной!❌\n\nГенерирую отчёт...", file_name
    else:
        return "✅Ссылка безопасна✅\n\nГенерирую отчёт...", file_name
