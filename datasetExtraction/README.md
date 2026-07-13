# Dataset Extraction Workflow

This folder contains the scripts and metadata we used to build and post-process the dataset.

## Overview

The workflow is run in this order:

1. `datasetextract.sh`
2. `manualclean.py`
3. `patch_all.sh`
4. `incofileInducer.sh`
5. `insertjunit.py`

Some steps require manual edits, especially for functions that do not compile or do not run.

## Required Input Files

### `index.csv`

`index.csv` is required by the extraction and patching workflow. It stores per-function metadata including:

- project
- author/owner and repository name
- commit hash
- function number in that commit
- simple function name
- Java file path where the function resides

This file is the central index that ties script steps to concrete functions in concrete commits.

### `dataset_mapping_dict.py`

`dataset_mapping_dict.py` contains the mapping from an original commit/function identifier to the commit/function identifier where it was fixed.

This mapping is used by parts of the evaluation pipeline that need to relate extracted cases to their fixed versions.

### `dataset_info.xlsx` (big table)

`dataset_info.xlsx` is the large framing table used during dataset preparation and manual correction.

It stores extended metadata for each case, including information such as the complete function header/signature and related framing fields that are needed to correct extraction artifacts manually.

## Step-by-Step Process

### 1) Run extraction

Execute the initial extraction step:

```zsh
cd ~/CASCADE/datasetExtraction
bash datasetextract.sh
```

This produces the first extracted dataset artifacts.

### 2) Manual clean

Run manual cleaning logic:

```zsh
cd ~/CASCADE/datasetExtraction
python manualclean.py
```

At this stage, use the metadata tables (`dataset_info.xlsx`) to correct obvious extraction issues.

### 3) Patch all

Run patching:

```zsh
cd ~/CASCADE/datasetExtraction
bash patch_all.sh
```

Important: for non-running or non-compiling projects, we had to manually provide/adjust files in the patching process.
Like deleting broken tests or renaming functions and classes that have since been added to java (like enum)

### 4) Induce inconsistency files

Run inconsistency file induction:

```zsh
cd ~/CASCADE/datasetExtraction
bash incofileInducer.sh
```

This step puts the files contain True or False if it is inconsistent into the right position

### 5) Insert JUnit

Run JUnit insertion:

```zsh
cd ~/CASCADE/datasetExtraction
python insertjunit.py
```

This finalizes dataset cases for downstream execution/evaluation stages by extracting the correct junit versions.

## Notes on Manual Intervention

- Non-compiling/non-running functions are expected and must be handled manually during `patch_all.sh`.
- `index.csv` is the primary lookup file to find the exact project, commit, function number, and source file path.
- The big table (`dataset_info.xlsx`) is used to verify and correct extracted framing details (for example, full headers/signatures).
- `dataset_mapping_dict.py` is needed for evaluation scenarios that compare original and fixed commits.
