import os

import click

from cpac_regression_dashboard.utils.parse_yaml import cpac_yaml


@click.command()
@click.option(
    "--pipeline1",
    required=True,
    type=str,
    help="Path to output directory from CPAC run " "to correlate against pipeline2",
)
@click.option(
    "--pipeline2",
    required=True,
    type=str,
    help="Path to output directory from CPAC run " "to correlate against pipeline1",
)
@click.option("--workspace", type=str, help="directory to save correlations")
@click.option("--branch", type=str, help="branch name")
@click.option("--data_source", type=str, help="Data site")
def main(pipeline1, pipeline2, workspace, branch, data_source) -> None:
    """Correlate outputs from regression run again another C-PAC version."""
    os.path.normpath(os.path.dirname(os.path.abspath(__file__)) + os.sep + os.pardir)
    run_name = f"{branch}_{data_source}"

    cpac_yaml(
        pipeline1,
        pipeline2,
        f"{workspace}/correlations",
        run_name,
        1,
        branch,
        data_source,
    )


if __name__ == "__main__":
    main()
