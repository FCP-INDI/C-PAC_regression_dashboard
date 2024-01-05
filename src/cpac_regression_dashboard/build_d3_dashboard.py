import os
from shutil import copy

import click
from lxml import etree


@click.command()
@click.option("--json_file", required=True, help="JSON file from correlations")
@click.option("--branch", required=True, help="branch name")
def main(json_file=None, branch=None):
    outdir = f"output/{branch}"
    os.makedirs(outdir, exist_ok=True)
    json_filename = os.path.basename(json_file)
    copy(json_file, "/".join([outdir, json_filename]))
    name = json_filename.replace(f"_{branch}.json", "")
    with open("templates/heatmap.html", "r", encoding="utf-8") as _f:
        body = etree.HTML(_f.read())
    script_element = etree.SubElement(body[0], "script")
    script_element.set("defer", "defer")
    script_element.set("src", "./heatmap.js")
    with open("templates/heatmap.js", "r", encoding="utf-8") as _f:
        with open(f"{outdir}/heatmap.js", "w", encoding="utf=8") as _s:
            _s.write(
                _f.read()
                .replace("DATAFILE", json_filename)
                .replace("GRAPHTITLE", branch)
                .replace("GRAPHSUBTITLE", name)
            )
    body = etree.tostring(body, encoding="unicode", method="html")

    with open(f"{outdir}/{name}.html", "w", encoding="utf-8") as _f:
        _f.write(body)

    return body, name, branch


if __name__ == "__main__":
    main()
