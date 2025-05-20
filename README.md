<b> Regression Dashboard </b>
=======================================================

This Github repo develops a report dashbaord on the automated regression tests from the repo <a href="https://github.com/cmi-dair/slurm_testing">slurm_testing</a>. This automated regression testing repo is specifically made for testing <a href="https://github.com/FCP-INDI">C-PAC</a>. Currently, the regression test only runs default pipeline.

<b> General </b>
=======================================================
- `pyproject.toml` commands must be run from one level above `src`
- Available commands:
  - `cpac_regsuite_create_yaml`
  - `cpac_regsuite_correlate`
  - `cpac_regsuite_generate_comment`


<b> Steps </b>
=======================================================

<b>1) Create Virtual Environment</b>
------------------------
- Any Python >= 3.9 should work
- <b>Command:</b> `uv venv --python 3.11 $FOLDER`

<b>2) Activate Virtual Environment</b>
------------------------
- <b>Command:</b> `source $FOLDER/bin/activate`

<b>3) Install Dashboard Repo</b>
------------------------
- <b>Command:</b> `uv pip install git+https://github.com/FCP-INDI/C-PAC_regression_dashboard.git`

<b>4) Create comparison YAML</b>
------------------------
- <b>Command:</b> `cpac_regsuite_create_yaml --pipeline1 OUTPUT-FOLDER_A --pipeline2 $OUTPUT_FOLDER_B --workspace {workspace_name} --branch {branch_name} --data_source {data_source}`
- `{workspace_name}`, `{branch_name}` and `{data_source}` can really be anything, they are mainly used to specify the exact pipeline output versions you are working with, in order to avoid confusion
- Output folders should be subject level, i.e. /`ocean/projects/med250004p/shared/regression_outputs_v1.8.7/ccs-options/KKI/sub-3884955` & `/ocean/projects/med250004p/shared/regression_outputs_v1.8.8/ccs-options/KKI/sub-3884955`
- <b>Output:</b>  `{branch_name}_{data_source}.yml` in the current working directory

<b>5) Calculate Correlations</b>
------------------------
- <b>Command:</b> `cpac_regsuite_correlate {branch_name}_{data_source}.yml`
- <b>Output:</b> `correlations/correlations.json` in the current working directory

<b>6) Build HTML Dashboard</b>
------------------------
- <b>Command:</b> `python3 build_d3_dashboard.py --json_file correlations.json --branch {branch_name}`
- <b>Output:</b> `correlations.json.html` in the current working directory


<b> Scripts </b>
=======================================================

<b>create_yml.py</b>
------------------------
This script parses through C-PAC output directories to find log, output, and working directories. These paths are written in a YAML file, which will get used in the following script for correlating. 

```
Arguments:

--pipeline1 {/path/to/CPAC/output}                CPAC output directory for correlating against `pipeline2`.
                                                  Its following subdirectory should be `log`, `output`
                                                  and `working`

--pipeline2 {/path/to/CPAC/output}                CPAC output directory for correlating against `pipeline1`.
                                                  Its following subdirectory should be `log`, `output`
                                                  and `working`.

--workspace $GITHUB_WORKSPACE                     Github workspace. Ensure that all files get saved here
                                                  for easy accessibility. 

--branch $GITHUB_BRANCH                           Developer's branch name. This ensures that all files created
                                                  have a unique name (no overwriting in cluster).

--data_source Site_Name                           Name of Site data comes from. Will be HNU_1, Site-CBIC, and Site-SI

Output:

{branch_name}.yml                                 YAML file that contains the file paths of CPAC output directories.

```

<b>calculate_correlations.py</b>
------------------------
This script calculates correlations of the files from the YAML file created above. These file paths contains images from the C-PAC output directories in which we want to correlate against. These JSON files are created in the cluster and must be sent back to Github Actions from the cluster when completed.

```
Arguments:

input_yaml {/path/to/branch_name.yml}             This is a positional argument!! Meaning there is no flag
                                                  so first argument must be the YAML file that was output
                                                  from `create_yml.py` 

--branch $GITHUB_BRANCH                           Developer's branch name. This ensures that all files created
                                                  have a unique name (no overwriting in cluster).

--data_source Site_Name                           Name of Site data comes from. Will be HNU_1, Site-CBIC, and Site-SI

Output:

{data_source}_{branch}.json                       The  output are JSON files with correlations of every file in the C-PAC
                                                  output directories.
```

<b>build_dashboard.py</b>
------------------------
This script builds the dashboard based on the correlations calculated above. Currently, the dashboard is saved onto a temporary HTML file that automatically opens up in a browser.

```
Arguments:

--json_files                                      JSON files created from `calculate_correlations.py` script.
                                                  If multiple JSON files, can separate then by a comma (NO SPACES).
                                                  --json_files HNU_1_{branch}.json,Site-SI_{branch}.json,Site-CBIC_{branch}.json

--branch $GITHUB_BRANCH                           Developer's branch name. This ensures that all files created
                                                  have a unique name (no overwriting in cluster).

Output:

temp.html                                         Temporary HTML file that automatically opens in browser. Tempoary
                                                  because it does not get saved to computer unless you save it.
                                                  If you exit browser, will need to build again.
```

<b>Flowchart of Scripts</b>
------------------------
![image](https://github.com/amygutierrez/regression_dashboard/assets/58920810/37400c11-8a85-4f4d-a0ff-d9feae4b467e)


<b>Dashboard Overview</b>
------------------------
The dashboard is a heat map where value < 0.98 will be red and value ≥ 0.98 will be green. 
Y-Axis: File names
X-Axis: Data Source (data Site name)

**Top part of Dashboard:**

<img width="1393" alt="Screen Shot 2023-07-24 at 9 56 09 PM" src="https://github.com/amygutierrez/regression_dashboard/assets/58920810/a536075e-ef76-4a14-93c2-def326de4dcf">
<br>
<br>

**Bottom X-Axis of Dashboard:** <br>

<img width="1147" alt="Screen Shot 2023-07-24 at 9 56 38 PM" src="https://github.com/amygutierrez/regression_dashboard/assets/58920810/ede1cac1-3391-4722-b689-900e575fdb13">
<br>

**Interactive:** <br>
If you hover over each block, it will also highlight the file name, Site name, and correlation value.

<img width="1293" alt="Screen Shot 2023-07-24 at 9 56 27 PM" src="https://github.com/amygutierrez/regression_dashboard/assets/58920810/8e4fc6ea-15c2-404c-8a6f-ff763269c056">


GIF!
---
![dashboard](https://github.com/amygutierrez/regression_dashboard/assets/58920810/a3f06150-f660-4362-be31-d9fd0e122f36)



