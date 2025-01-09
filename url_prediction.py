import pandas

from joblib import load

from url_classification import get_metrics


model = load('./model/random_forest_model.pkl')

url_metric = get_metrics("https://www.kaggle.com/datasets/taruntiwarihp/phishing-site-urls")
# url_metric = get_metrics("http://login.live.com.skyhigh9157.ms-office-365-email.skyhigh9157.myshn.net/")

print(url_metric)

if url_metric:
    metrics = {
        'length_url': [url_metric['length_url']],
        'length_hostname': [url_metric['length_hostname']],
        'is_ip': [url_metric['is_ip']],
        'dots_qty': [url_metric['dots_qty']],
        'hyphens_qty': [url_metric['hyphens_qty']],
        'at_qty': [url_metric['at_qty']],
        'is_www': [url_metric['is_www']],
        'is_https': [url_metric['is_https']],
        'is_tld': [url_metric['is_tld']],
        'suspicious_subdomains': [url_metric['suspicious_subdomains']],
        'subdomains_qty': [url_metric['subdomains_qty']],
        'is_short_url': [url_metric['is_short_url']],
        'path_extension': [url_metric['path_extension']],
        'has_redirection': [url_metric['has_redirection']],
        'suspicious_top_level_domain': [url_metric['suspicious_top_level_domain']],
        'qty_hyperlinks': [url_metric['qty_hyperlinks']],
        'proportion_extHyperlinks': [url_metric['proportion_extHyperlinks']],
        'is_login_form': [url_metric['is_login_form']],
        'is_external_favicon': [url_metric['is_external_favicon']],
        'iframe': [url_metric['iframe']],
        'is_empty_title': [url_metric['is_empty_title']],
        'whois_registered_domain': [url_metric['whois_registered_domain']],
        'domain_age': [url_metric['domain_age']]
    }

    df_metrics = pandas.DataFrame(metrics)

    df_metrics_values = df_metrics.values

    prediction = model.predict(df_metrics_values)

    if prediction[0] == 1:
        print("Ссылка является фишинговой")
    else:
        print("Ссылка безопасна")
