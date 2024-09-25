import json


def dataset(name: str, data_source: str, value: float | int | str) -> str:
    return f"""
        {{
            "rowid": "{name}",
            "columnid": "{data_source}",
            "value": "{value}"
        }},
            """


def body(all_keys: list[str], data_source: str) -> str:
    data_body: str = "["
    for key in all_keys:
        name_value = key.split(": ")
        name = name_value[0]
        value = name_value[1]
        data_body += dataset(name, data_source, value)
    data_body = data_body.strip()
    data_body += "]"
    return json.dumps(json.loads(data_body))


def write_html(data_body) -> str:
    return f"""
    <html>
    <head>
        <title>Correlations</title>
        <script type="text/javascript" src="https://cdn.fusioncharts.com/fusioncharts/latest/fusioncharts.js"></script>
        <script type="text/javascript" src="https://cdn.fusioncharts.com/fusioncharts/latest/themes/fusioncharts.theme.fusion.js"></script>
        <script type="text/javascript">
            FusionCharts.ready(function(){{
            var chartObj = new FusionCharts({{
        type: 'heatmap',
            renderAt: 'chart-container',
                width: '100%',
                    height: '2000',
                        dataFormat: 'json',
                            dataSource: {{
            "chart": {{
                "caption": "Regression Correlations",
                    "subcaption": "By Features",
                        "xAxisName": "Features",
                            "yAxisName": "Model",
                                "showplotborder": "1",
                                    "showValues": "1",
                                        "xAxisLabelsOnTop": "1",
                                            "plottooltext": "<div id='nameDiv' style='font-size: 12px; border-bottom: 1px dashed #666666; font-weight:bold; padding-bottom: 3px; margin-bottom: 5px; display: inline-block; color: #888888;' >$rowLabel :</div>{{br}}Rating : <b>$dataValue</b>{{br}}$columnLabel : <b>$tlLabel</b>{{br}}<b>$trLabel</b>",
                                                //Cosmetics
                                                "baseFontColor": "#333333",
                                                    "baseFont": "Helvetica Neue,Arial",
                                                        "toolTipBorderRadius": "2",
                                                            "toolTipPadding": "5",
                                                                "theme": "fusion"
            }},
            "dataset" : [{{
                "data": [
                    {data_body}
                ]
            }}],
                "colorrange": {{
                "gradient": "0",
                    "minvalue": "0",
                        "code": "E24B1A",
                            "startlabel": "Poor",
                                "endlabel": "Good",
                                    "color": [{{
                                        "code": "E24B1A",
                                        "minvalue": "0",
                                        "maxvalue": "0.979",
                                        "label": "Bad"
                                    }}, {{
                                        "code": "6DA81E",
                                        "minvalue": "0.98",
                                        "maxvalue": "1.1",
                                        "label": "Good"
                                    }}]
            }}
        }}
    }}
    );
                chartObj.render();
            }});
        </script>
        </head>
        <body>
            <div id="chart-container">Correlations heatmap will load here!</div>
        </body>
    </html>
    """  # noqa: E501


def setup_browser(html_template) -> None:
    import tempfile
    import webbrowser

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as temp_file:
        temp_file.write(html_template.encode("utf-8"))
        filename = "file:///" + temp_file.name
        webbrowser.open_new_tab(filename)
