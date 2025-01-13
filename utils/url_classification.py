import re
import whois
import pandas
import requests
import tldextract


def get_metrics(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            pass
        else:
            print(f"Сайт {url} не доступен. Статус: {response.status_code}")
            return
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при попытке получить сайт {url}: {e}")
        return

    metrics = {}

    metrics['length_url'] = len(url)

    extracted_url = tldextract.extract(url)

    metrics['length_hostname'] = len(extracted_url.domain) + len(extracted_url.suffix)

    metrics['is_ip'] = 1 if re.match(r'\d+\.\d+\.\d+\.\d+', url) else 0

    metrics['dots_qty'] = url.count(".")
    metrics['hyphens_qty'] = url.count("-")
    metrics['at_qty'] = url.count("@")

    metrics['is_www'] = 1 if "www" in url else 0
    metrics['is_https'] = 1 if url.startswith("https") else 0
    metrics['is_tld'] = 1 if extracted_url.suffix else 0

    metrics['suspicious_subdomains'] = 1 if len(extracted_url.subdomain) > 20 else 0
    metrics['subdomains_qty'] = extracted_url.subdomain.count(".") + 1 if extracted_url.subdomain else 0

    check_is_short_url = extracted_url.domain + "." + extracted_url.suffix
    with open("./metrics/url_shorteners_list.txt", "r", encoding="UTF-8") as url_shortener_list: 
        metrics['is_short_url'] = 0  
        for line in url_shortener_list:
            if check_is_short_url == line.strip():
                metrics['is_short_url'] = 1
                break

    extensions = [
        ".html", ".htm", ".xhtml", ".php", ".js", ".css",
        ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", 
        ".webp", ".tiff", ".mp3", ".wav", ".ogg", ".aac", 
        ".flac", ".mp4", ".avi", ".mov", ".mkv", ".wmv", 
        ".flv", ".pdf", ".doc", ".docx", ".xls", ".xlsx", 
        ".ppt", ".pptx", ".txt", ".csv", ".zip", ".rar", 
        ".tar", ".gz", ".7z", ".json", ".xml", ".bin", 
        ".sql", ".yaml", ".md"
    ]

    metrics['path_extension'] = 0
    last_part = url.split('/')[-1]
    for ext in extensions:
        if last_part.endswith(ext):
            metrics['path_extension'] = 1

    metrics['has_redirection'] = url.count('//') - 1

    check_is_suspicious_tld = extracted_url.suffix
    with open("./metrics/suspicious_tld_list.txt", "r", encoding="UTF-8") as suspicious_tld_list: 
        metrics['suspicious_top_level_domain'] = 0  
        for tld in suspicious_tld_list:
            if check_is_suspicious_tld == tld.strip()[2:]:
                metrics['suspicious_top_level_domain'] = 1
                break

    try:
        response = requests.get(url)
        content = response.text
        metrics['qty_hyperlinks'] = content.count('<a ')
        metrics['proportion_extHyperlinks'] = metrics['qty_hyperlinks'] / (len(content.split()) + 1)
    except requests.exceptions.RequestException:
        metrics['qty_hyperlinks'] = 0
        metrics['proportion_extHyperlinks'] = 0

    if content:
        metrics['is_login_form'] = 1 if 'login' in content else 0
        metrics['is_external_favicon'] = 0
        metrics['iframe'] = 1 if '<iframe' in content else 0
        metrics['is_empty_title'] = 1 if re.search(r'<title>\s*</title>', content) else 0
    else:
        metrics['is_login_form'] = 0
        metrics['is_external_favicon'] = 0
        metrics['iframe'] = 0
        metrics['is_empty_title'] = 0   

    whois_check = extracted_url.domain + "." + extracted_url.suffix
    w = whois.whois(whois_check)

    metrics['whois_registered_domain'] = 1 if w.domain_name else 0

    if w.creation_date:
        if isinstance(w.creation_date, list):
            creation_date = w.creation_date[0]
        else:
            creation_date = w.creation_date

        metrics['domain_age'] = (pandas.to_datetime('now') - pandas.to_datetime(creation_date)).days
    else:
        metrics['domain_age'] = -1

    return(metrics)
