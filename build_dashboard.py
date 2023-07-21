from utils.html_script import write_html, setup_browser

import os
import click

def process_option(ctx, param, value):
    if value is not None:
        values = value.split(',')
        return [val.strip() for val in values]

@click.command()
@click.option('--json_files', required=True, 
              callback=process_option, help='JSON files from correlations')
@click.option('--branch', required=True, help='branch name')

def main(json_files=None, branch=None):
    body = ''
    data_source = []
    for json in json_files:
        name = os.path.basename(json)
        data = name.replace(f"_{branch}.json", '')
        data_source.append(data)
        with open(json) as user_file:
            file_contents = user_file.read()
            body += file_contents
    body = (body.rstrip()).rstrip(",")

    html_body = write_html(body)
    file = open('html.html', 'w')
    file.write(html_body)
    file.close()
    setup_browser(html_body)

    return body, data_source, branch

if __name__ == "__main__":
    main()