#!/usr/bin/env python
"""Calculate correlations and write them to D3-friendly file"""
from cpac_correlations import cpac_correlations

from utils.html_script import body

if __name__ == "__main__":
    all_keys, data_source, branch = cpac_correlations()
    html_body = body(all_keys, data_source)
    with open(f"{data_source}_{branch}.json", "w", encoding="utf-8") as file:
        file.write(html_body)
