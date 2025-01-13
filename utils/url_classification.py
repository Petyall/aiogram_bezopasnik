import re
import whois
import aiohttp
import tldextract
import pandas as pd


async def fetch_url_content(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                response.raise_for_status()
                return await response.text()
    except Exception as e:
        print(f"Ошибка при попытке получить сайт {url}: {e}")
        return None


async def get_metrics(url):
    content = await fetch_url_content(url)
    if content is None:
        return None

    metrics = {}
    extracted_url = tldextract.extract(url)

    metrics['length_url'] = len(url)
    metrics['length_hostname'] = len(extracted_url.domain) + len(extracted_url.suffix)
    metrics['is_ip'] = int(bool(re.match(r'\d+\.\d+\.\d+\.\d+', url)))
    metrics['dots_qty'] = url.count(".")
    metrics['hyphens_qty'] = url.count("-")
    metrics['at_qty'] = url.count("@")
    metrics['is_www'] = int("www" in url)
    metrics['is_https'] = int(url.startswith("https"))
    metrics['is_tld'] = int(bool(extracted_url.suffix))

    metrics['suspicious_subdomains'] = int(len(extracted_url.subdomain) > 20)
    metrics['subdomains_qty'] = extracted_url.subdomain.count(".") + 1 if extracted_url.subdomain else 0

    check_is_short_url = f"{extracted_url.domain}.{extracted_url.suffix}"
    with open("./metrics/url_shorteners_list.txt", "r", encoding="UTF-8") as file:
        metrics['is_short_url'] = int(any(check_is_short_url == line.strip() for line in file))

    extensions = [
        ".html", ".php", ".jpg", ".png", ".mp3", ".mp4", ".pdf", ".docx", ".zip", ".json", ".xml"
    ]
    last_part = url.split('/')[-1]
    metrics['path_extension'] = int(any(last_part.endswith(ext) for ext in extensions))

    metrics['has_redirection'] = url.count('//') - 1

    check_is_suspicious_tld = extracted_url.suffix
    with open("./metrics/suspicious_tld_list.txt", "r", encoding="UTF-8") as file:
        metrics['suspicious_top_level_domain'] = int(
            any(check_is_suspicious_tld == line.strip()[2:] for line in file)
        )

    metrics['qty_hyperlinks'] = content.count('<a ')
    metrics['proportion_extHyperlinks'] = metrics['qty_hyperlinks'] / (len(content.split()) + 1)
    metrics['is_login_form'] = int('login' in content)
    metrics['is_external_favicon'] = 0
    metrics['iframe'] = int('<iframe' in content)
    metrics['is_empty_title'] = int(bool(re.search(r'<title>\s*</title>', content)))

    try:
        whois_data = whois.whois(f"{extracted_url.domain}.{extracted_url.suffix}")
        metrics['whois_registered_domain'] = int(bool(whois_data.domain_name))
        creation_date = whois_data.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        metrics['domain_age'] = (
            (pd.to_datetime('now') - pd.to_datetime(creation_date)).days
            if creation_date else -1
        )
    except Exception as e:
        print(f"Ошибка WHOIS для {url}: {e}")
        metrics['whois_registered_domain'] = 0
        metrics['domain_age'] = -1

    return metrics