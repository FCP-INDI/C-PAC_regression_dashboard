#!/usr/bin/env python
"""Calculate correlations and write them to D3-friendly file."""
import json

from cpac_correlations import cpac_correlations

from cpac_regression_dashboard.utils.html_script import body


def main() -> None:
    """Gather correlation coefficients and write them to D3-readable JSON."""
    all_keys, data_source, branch = cpac_correlations()
    html_body = body(all_keys, data_source)
    with open(f"{data_source}_{branch}.json", "w", encoding="utf-8") as file:
        file.write(json.dumps(json.loads(f"[{html_body.strip().strip(',')}]")))


main.__doc__ = __doc__

if __name__ == "__main__":
    main()
