"""From a pair of CPAC output directories, write a YAML file for regression."""
import os
from typing import Optional, Union

import yaml

_PIPELINE_DICT = dict[Optional[str], dict[str, Optional[Union[str, int]]]]
_FULL_YAML_DICT = dict[
    str, Union[dict[str, Union[bool, int, Optional[str]]], _PIPELINE_DICT]
]


def get_dir(paths: str) -> Optional[str]:
    """Get the full path to a ``pipeline_*`` directory."""
    if not paths:
        directory = None
    else:
        for root, dirs, files in os.walk(paths):
            for _dir in dirs:
                if "pipeline_" in _dir:
                    directory = os.path.join(root, _dir)
    return directory


def write_pipeline_yaml(
    output_dir: Optional[str] = None,
    working_dir: Optional[str] = None,
    log_dir: Optional[str] = None,
    pipeline_config: Optional[str] = None,
    pipeline_name: Optional[str] = None,
) -> _PIPELINE_DICT:
    """Collect paths and strings to write."""
    return {
        pipeline_name: {
            "output_dir": output_dir,
            "work_dir": working_dir,
            "log_dir": log_dir,
            "pipe_config": pipeline_config,
            "replacements": None,
        }
    }


def parse_yaml(directory: str, pipeline_name: str) -> _PIPELINE_DICT:
    """Parse a CPAC output directory for pipeline information."""
    subdirs = ["log", "working", "output"]
    paths: dict[str, Optional[str]] = {}

    for subdir in subdirs:
        if os.path.isdir(os.path.join(directory, subdir)):
            paths[f"{subdir}_dir"] = os.path.join(directory, subdir)
        else:
            paths[f"{subdir}_dir"] = None
    assert isinstance(paths["log_dir"], str)
    log_dir: Optional[str] = get_dir(paths["log_dir"])

    if log_dir is not None:
        for root, _dirs, files in os.walk(paths["log_dir"]):
            for file in files:
                if file.endswith("Z.yml"):
                    pipeline_config = os.path.join(root, file)
    assert isinstance(paths["working_dir"], str)
    working_dir = get_dir(paths["working_dir"])
    assert isinstance(paths["output_dir"], str)
    output_dir = get_dir(paths["output_dir"])

    return write_pipeline_yaml(
        output_dir, working_dir, log_dir, pipeline_config, pipeline_name
    )


def write_yaml(
    pipeline_1: _PIPELINE_DICT,
    pipeline_2: _PIPELINE_DICT,
    correlations_dir: Optional[str] = None,
    run_name: Optional[str] = None,
    n_cpus: Optional[int] = None,
) -> _FULL_YAML_DICT:
    """Combine settings and both pipelines into a single dictionary."""
    yaml_dict: _FULL_YAML_DICT = {}
    yaml_dict["settings"] = {
        "n_cpus": n_cpus,
        "correlations_dir": correlations_dir,
        "run_name": run_name,
        "s3_creds": None,
        "quick": False,
        "verbose": False,
    }

    yaml_dict["pipelines"] = {**pipeline_1, **pipeline_2}

    return yaml_dict


def cpac_yaml(
    pipeline1: str,
    pipeline2: str,
    correlations_dir: str,
    run_name: str,
    n_cpus: int,
    branch: str,
    data_source: str,
) -> None:
    """Write a YAML file for the regression run."""
    pipeline_1 = parse_yaml(pipeline1, "pipeline_1")
    pipeline_2 = parse_yaml(pipeline2, "pipeline_2")

    yaml_contents = write_yaml(
        pipeline_1, pipeline_2, correlations_dir, run_name, n_cpus
    )

    with open(f"{branch}_{data_source}.yml", "w") as file:
        yaml.dump(yaml_contents, file, default_flow_style=False, sort_keys=False)