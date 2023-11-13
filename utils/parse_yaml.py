import os

import yaml


def get_dir(paths):
    if not paths:
        directory = None
    else:
        for root, dirs, files in os.walk(paths):
            for dir in dirs:
                if "pipeline_" in dir:
                    directory = os.path.join(root, dir)
    return directory


def write_pipeline_yaml(
    output_dir=None,
    working_dir=None,
    log_dir=None,
    pipeline_config=None,
    pipeline_name=None,
):
    pipeline = {
        pipeline_name: {
            "output_dir": output_dir,
            "work_dir": working_dir,
            "log_dir": log_dir,
            "pipe_config": pipeline_config,
            "replacements": None,
        }
    }

    return pipeline


def parse_yaml(directory=None, pipeline_name=None):
    subdirs = ["log", "working", "output"]
    paths = {}

    for subdir in subdirs:
        if os.path.isdir(os.path.join(directory, subdir)):
            paths[f"{subdir}_dir"] = os.path.join(directory, subdir)
        else:
            paths[f"{subdir}_dir"] = None

    log_dir = get_dir(paths["log_dir"])

    for root, dirs, files in os.walk(paths["log_dir"]):
        for file in files:
            if file.endswith("Z.yml"):
                pipeline_config = os.path.join(root, file)

    working_dir = get_dir(paths["working_dir"])
    output_dir = get_dir(paths["output_dir"])

    pipeline_dict = write_pipeline_yaml(
        output_dir, working_dir, log_dir, pipeline_config, pipeline_name
    )

    return pipeline_dict


def write_yaml(
    pipeline_1=None, pipeline_2=None, correlations_dir=None, run_name=None, n_cpus=None
):
    yaml_dict = {}
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
    pipeline1, pipeline2, correlations_dir, run_name, n_cpus, branch, data_source
):
    pipeline_1 = parse_yaml(pipeline1, "pipeline_1")
    pipeline_2 = parse_yaml(pipeline2, "pipeline_2")

    yaml_contents = write_yaml(
        pipeline_1, pipeline_2, correlations_dir, run_name, n_cpus
    )

    with open(f"{branch}_{data_source}.yml", "w") as file:
        yaml.dump(yaml_contents, file, default_flow_style=False, sort_keys=False)

    return
