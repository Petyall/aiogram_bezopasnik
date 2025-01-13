import time

from jinja2 import Template


async def generate_html_report(url, metrics, is_phishing):
    html_template = """
        <html>
            <head>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
                <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
                <style>
                    body { font-family: Arial, sans-serif; }
                    .url-display { text-align: center; padding: 20px; margin: 20px 0; }
                    .legitimate { color: green; font-weight: bold; }
                    .phishing { color: red; font-weight: bold; }
                    .content-row { display: flex; justify-content: space-between; margin-top: 20px; }
                    .content-row > div { flex: 1; margin: 0 10px; }
                    .heat-map { width: 100%; height: 30px; margin: 10px 0; position: relative; }
                    .heat-map-left { background: linear-gradient(to left, #00ff00, #ff0000); }
                    .heat-map-right { background: linear-gradient(to right, #00ff00, #ff0000); }
                    .marker { position: absolute; width: 2px; height: 30px; background: black; top: 0; }
                    .parameter-list { list-style: none; padding: 0; }
                </style>
            </head>
            <body>
                <div class="container mt-5">
                    <div class="url-display">
                        <div id="url" class="{{ is_phishing }}"><h1>{{ url }}</h1></div>
                    </div>
                    <div class="content-row">
                        <div>
                            <canvas id="pieChart"></canvas>
                        </div>
                        <div>
                            <ul class="list-group parameter-list">
                                {% for label, value in parameter_data.items() %}
                                    <li class="list-group-item">{{ label }}: {{ '✔️' if value == 1 else '❌' }}</li>
                                {% endfor %}
                            </ul>
                        </div>
                        <div>
                            <ul>
                                {% for label, (value, min_value, max_value, rotation) in heatmap_data.items() %}
                                    <li class="mb-4">
                                        <h6>{{ label }} ({{ value }})</h6>
                                        <div class="heat-map {{ rotation }}">
                                            {% set position = 100 * (value - min_value) / (max_value - min_value) %}
                                            <div class="marker" style="left: {{ position if rotation == 'heat-map-right' else 100 - position }}%;"></div>
                                        </div>
                                        <small>Минимум: {{ min_value }} | Максимум: {{ max_value }}</small>
                                    </li>
                                {% endfor %}
                            </ul>
                        </div>
                    </div>
                </div>
                <script>
                    const ctx = document.getElementById('pieChart').getContext('2d');
                    const pieData = {{ pie_data | tojson }};
                    new Chart(ctx, {
                        type: 'pie',
                        data: {
                            labels: Object.keys(pieData),
                            datasets: [{
                                data: Object.values(pieData),
                                backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF']
                            }]
                        },
                        options: {
                            responsive: true,
                            plugins: { legend: { position: 'bottom' } }
                        }
                    });
                </script>
            </body>
        </html>
    """

    pie_data = {
        'Количество "."': metrics['dots_qty'],
        'Количество "-"': metrics['hyphens_qty'],
        'Количество "@"': metrics['at_qty'],
        'Количество поддоменов': metrics['subdomains_qty'],
        'Количество внешних ссылок': metrics['qty_hyperlinks']
    }

    parameter_data = {
        'Ссылка - IP?': metrics['is_ip'],
        'Это сокращенная ссылка?': metrics['is_short_url'],
        'Есть ли информация о домене в WHOIS?': metrics['whois_registered_domain'],
        'В ссылке есть www?': metrics['is_www'],
        'В ссылке есть https?': metrics['is_https'],
        'В ссылке есть расширения файлов?': metrics['path_extension'],
        'В ссылке есть домен верхнего уровня?': metrics['is_tld'],
        'В ссылке есть подозрительные поддомены?': metrics['suspicious_subdomains'],
        'На сайте есть iframe?': metrics['iframe'],
        'На сайте есть форма авторизации?': metrics['is_login_form'],
        'У сайта пустой заголовок?': metrics['is_empty_title'],
        'У сайта сторонняя иконка (favicon)?': metrics['is_external_favicon']
    }

    heatmap_data = {
        'Подозрительные домены': (metrics['suspicious_top_level_domain'], 0, 10, 'heat-map-right'),
        'Отношение внешних ссылок': (metrics['proportion_extHyperlinks'], 0, 1, 'heat-map-right'),
        'Возраст домена': (metrics['domain_age'], 0, 10000, 'heat-map-left')
    }

    template = Template(html_template)
    html_content = template.render(
        url=url,
        is_phishing=is_phishing,
        pie_data=pie_data,
        parameter_data=parameter_data,
        heatmap_data=heatmap_data
    )

    file_name = f"report_{int(time.time())}.html"
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(html_content)

    return file_name
