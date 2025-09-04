"""From a pair of CPAC output directories, write a YAML file for regression."""
import os
from pathlib import Path
from typing import cast, Optional

import yaml

_PIPELINE_DICT = dict[Optional[str], dict[str, Optional[int | str]]]
_FULL_YAML_DICT = dict[str, dict[str, bool | int | Optional[str]] | _PIPELINE_DICT]


def get_dir(paths: Optional[str], variable_name: str = "dir") -> Optional[str]:
    """Get the full path to a ``pipeline_*`` directory."""
    if paths is None:
        return None
    assert isinstance(paths, str), f"{variable_name}: {paths}"
    directory = paths
    if directory:
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
    log_dir = get_dir(paths["log_dir"], "log_dir")
    pipeline_config = None
    if log_dir is not None:
        for root, _dirs, files in os.walk(log_dir):
            for file in files:
                if file.endswith("Z.yml"):
                    pipeline_config = os.path.join(root, file)
    working_dir = get_dir(paths["working_dir"], "working_dir")
    output_dir = get_dir(paths["output_dir"], "output_dir")

    return write_pipeline_yaml(
        output_dir, working_dir, log_dir, pipeline_config, pipeline_name
    )


def write_yaml(
    pipeline_1: _PIPELINE_DICT,
    pipeline_2: _PIPELINE_DICT,
    correlations_dir: str,
    run_name: str,
    n_cpus: int = 1,
) -> _FULL_YAML_DICT:
    """Combine settings and both pipelines into a single dictionary."""
    yaml_dict: _FULL_YAML_DICT = {}
    yaml_dict["settings"] = cast(
        dict[str, bool | int | Optional[str]] | _PIPELINE_DICT,
        {
            "n_cpus": int(n_cpus),
            "correlations_dir": correlations_dir,
            "run_name": run_name,
            "s3_creds": None,
            "quick": False,
            "verbose": False,
        },
    )

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
) -> Path:
    """Write a YAML file for the regression run."""
    pipeline_1: _PIPELINE_DICT = parse_yaml(pipeline1, "pipeline_1")
    pipeline_2: _PIPELINE_DICT = parse_yaml(pipeline2, "pipeline_2")

    yaml_contents: _FULL_YAML_DICT = write_yaml(
        pipeline_1, pipeline_2, correlations_dir, run_name, n_cpus
    )

    yaml_path: Path = Path(f"{branch}_{data_source}.yml")
    """Path to YAML file for regression correlation."""
    with yaml_path.open("w") as file:
        yaml.dump(yaml_contents, file, default_flow_style=False, sort_keys=False)
    return yaml_path
