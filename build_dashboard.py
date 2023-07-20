import click

def process_option(ctx, param, value):
    if value is not None:
        values = value.split(',')
        return [val.strip() for val in values]

@click.command()

@click.option('--json_files','-o', required=True, 
              callback=process_option, help='JSON files from correlations')
@click.option('--data_source','-o', required=True, 
              callback=process_option, help='data type')
@click.option('--branch','-o', required=True, 
              callback=process_option, help='branch name')


def main(json_files=None, data_source=None, branch=None):
    body = ''
    for json in json_files:
            with open(f"{data_source}_{branch}.json") as user_file:
                file_contents = user_file.read()
                body += file_contents
    return body

if __name__ == "__main__":
    all_keys, data_source, branch = main()
    html_body = body(all_keys, data_source)
    file = open(f"{data_source}_{branch}.json","w")
    file.write(html_body)
    file.close()