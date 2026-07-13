
## 1  Overview
This folder contains everything needed to reproduce the results, tables and graphs for our 2026 FSE Paper: 
"Cascade: Detecting Inconsistencies between Code and Documentation with Automatic Test Generation"

The code is organized so that you can either **re-run the complete benchmark end-to-end** (Section 3) or 
**inspect the pre-computed results** shown in the paper (for that skip to Section 4).

The main tool of our work is CASCADE, but for the benchmark we also compare it to several baselines. 
Some basic LLM baselines and the existing tools DocChecker [1] and C4RLLaMA [2].

DocChecker code was adjusted from here: <https://github.com/FSoft-AI4Code/DocChecker>
C4RLLaMA code from here: <https://github.com/aiopsplus/C4RLLaMA>


## 2  Dataset format (`dataset.zip`)
To get a internal validation we collected a dataset of inconsistent and consistent Doc-code pairs. 
This is stored in `dataset.zip`.
After unzipping, you will find the structure shown below; it mirrors GitHub projects down to individual inconsistent/fixed methods:


```
java/
  <project-owner>/
    <project-name>/
      <commit-SHA>/
        [file.patch]      # patch to make this specific commit buildable
        <idx>/            # Numerical index of method inside the commit (sometimes there are several inconsistent methods in the same commit) c1, c2 etc. are the extra consistent samples
          analyzed.json     # extensive method metadata (see below)
          inconsistency.txt # "True" / "False" – is there an inconsistency?
```

Note, 'coreDataset.zip' contains only the core pairwise 71 inconsistent and 71 consistent samples. (much smaller and faster to run)

* **`dataset_mapping_dict.py`** a file that maps each commit to its fixed/inconsistent counterpart. This is needed to calculate the PFP Metric.


each sample contains a `analyzed.json` file which contains:
  * extracted Javadoc & signature
  * fully-qualified class name, neighbor methods in the same class, constructors, fields – everything a analysis tool might need
  * the code body
  * original unit tests (if any existed) and JUnit version


## 3  Running the benchmark from scratch

> All paths below assume you call commands from inside **`PaperEvaluation/`**.

### 3.1 Prerequisites

* Python ≥ 3.10 with pip and venv
* `git`, `unzip`, `curl` (for repository & dataset handling)
* Linux/macOS – (Windows was not tested)

### 3.2 setup

CASCADE and LLM-Baseline require an OpenAi API key in the environment
  
   ```bash
   export OPENAI_API_KEY=<your key>
   ```

you can execute the `prepare_experiments.sh` script to prepare all venvs and build CASCADE

   ```bash
    bash ./prepare_experiments.sh
   ```


**WARNING**
if you have no available GPU, the C4RLLaMA baseline will probably not be able to run and you will also have to change line 35 in the file `PaperEvaluation\drivers\DocChecker\DocChecker\DocCheckerNet.py`

from: 

  ```python
   model_to_load.load_state_dict(torch.load(output_dir,map_location='cuda:0') )
  ```
to:

  ```python
   model_to_load.load_state_dict(torch.load(output_dir, map_location=torch.device('cpu')))
  ```

The retrained model for DocChecker and the re-trained fine-tuned weights for C4RLLaMA are to big for Git
So they are published on figshare. You have to download them and put them in the correct folders.

**DocChecker**
Download bin https://figshare.com/s/981c2fbe830b905b01a9
and put it in `/drivers/DocChecker/pretrained_model`

**C4RLLaMA**
Download zip from https://figshare.com/s/812541da6a1f33025f69
and put content in `/drivers/C4RLLaMA/weights`


### 3.3 Execute all drivers

1. make sure you are in the directory `PaperEvaluation`
2. Run:

   ```bash
   bash ./run.sh
   ```
   
   in this script you can change which drivers to run; in the 9th line:  e.g.   `DRIVERS_LIST=("CASCADE" "Baseline")` for cascade and the baseline or   `DRIVERS_LIST=()`runs everything (names have to match the folder names in the driver folder)

   The script will:

   * unzip the dataset into folder `java`;
   * iterate over every commit; for each commit:
     * clone the project repo, checkout the specific commit;
     * apply `file.patch` if present so the build succeeds;
     * for each driver (CASCADE, DocChecker, C4RLLaMA, Baseline):
       * copy everything in the respective folder into the current test folder.
       * execute the driver.sh `driver/<name>/driver.sh` (tool-specific wrapper);
       * these then usually call the tools via python with the correct venv and generate a results file
     * save this tool’s output to `result_<tool>.txt`.
   * clean up temporary artifacts.

The results will be contained throughout the `java` folder. This folder follows the same structure as `dataset.zip` but under each sample now has several result and log files for the different tools.

### 3.4 Evaluate metrics

This script `eval.py` goes through the folder `java` in which the results are situated. 
Metrics (precision, recall, F1, *etc.*) are printed to stdout. 
This script was also used to create all the graphics in the Paper.

you will need matplotlib installed for it to run. it is contained in the cascade venv, so you can run it with 
`./cascade.venv/bin/python3 eval.py` or install it in your global python environment with `pip install matplotlib` and then run `python3 eval.py`


Some helpful command line arguments for `eval.py`:

Basic results over EVERYTHING (all metrics and versions of baselines even those not used in the final paper: 
```
python3 eval.py c b c4 d     # c=CASCADe, d=DocChecker, b=baseline, c4=C4RLLaMA
```

If we want an unbalanced split of the dataset we have to specify how often we want to sample consistent samples. thats what the --c flag is for. 
the dataset contains over 800 extra consistent samples. the pairwise 71 pairs of consistent and inconsistent samples are always included. 
If you want additional consistent ones to be checked out you have to specify the amount with the --c flagg.

For example if you want double the amount of consistent samples you have to specify `--c 71`

the script then calculates the metrics including 71 inconsistent and 142 consistent samples. 
It randomly picks 71 from the 800 consistent samples 1000 times and reports the averages (and std deviation)) of the metrics.

```
python3 eval.py c --c 71
```
(note this may take some time.)


The script also has a plot mode to generate the plots shown in the paper.
e.g.:

```
python3 eval.py --plot \
  --plot-points 0="50% (71)" 36="60% (107)" 95="70% (166)" 213="80% (284)" 568="90% (639)"  --plot-series 'c4:singleLines=C4RLLaMMA' 'd:singleLines=DocChecker' 'b:atLeast3=Baseline≥3' 'c:nop2f=CASCADE' --plot-metric Prec --plot-stat median --seed 42 --plot-out prec.pdf
```

--plot : enter plot mode
\
--plot-points : specifies the labels for the x axis and the amount of consistent samples that should be included for each plot point.
\
--plot-series : specifies the series to be plotted. The format is <tool-prefix>:<label> where tool-prefix is the prefix of the tool as specified in the results files (e.g. c for cascade, b for baseline, d for docchecker) and label is the label that should be shown in the legend for this series.
\
--plot-metric : which metric to plot (e.g. Prec, Rec, F1, ...)
\
--plot-stat : which metric to plot (e.g. median, mean)
\
--seed : seed for random sampling
\
--plot-out : specifies the output file for the plot.




---

## 4  Using the pre-computed results

If you only want to inspect the results reported in the paper:

The results zip file is to large For Git and can only be obtained from the Zenodo version of the repo.
https://zenodo.org/records/19483108


1. Unzip **`results.zip`** (contains one folder called `java`) next to to `eval.py` script. (Unpacked size is 1GB)
2. Run the same commands as shown in 3.4 (`python3 eval.py c d b c4`).

More information is also available e.g.:
   * CASCADE's-generated tests are now inside each `analyzed.json` under the key **`new_tests`**.
   * Complete LLM answers for the baselines are stored in **`log_baseline.txt`**.

This prints the results for RQ1 and RQ2. RQ3 has no disclosable results other than the reported issues.
(RQ2 results are the different shown versions of CASCADE)

---


## 5  Troubleshooting & FAQ

* **Tree-sitter fails to compile** – ensure you have a C toolchain (`gcc` / `clang`) installed.
* **CUDA not found** – use the CPU fallback shown in Section 4.2.
* **OPENAI_API_KEY not picked up** – confirm the openai key is exported *in the same shell session* that runs `run.sh`.

---


[1] Dau, Anh, et al. "Docchecker: Bootstrapping code large language model for detecting and resolving code-comment inconsistencies." Proceedings of the 18th Conference of the European Chapter of the Association for Computational Linguistics: System Demonstrations. 2024.\
[2] Rong, Guoping, et al. "Code comment inconsistency detection and rectification using a large language model." Proceedings of the IEEE/ACM 47th International Conference on Software Engineering. 2025.