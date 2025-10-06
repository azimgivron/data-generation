# 🧬 OMIM Dataset Generation

This repository provides a simple workflow to **generate a structured OMIM gene–disease association dataset** from the official **OMIM GeneMap2** file.
The process parses raw OMIM data, filters it, and outputs a clean dataset suitable for downstream analysis.

---

## ⚙️ Setup

### 1. Create a Virtual Environment

```bash
python3 -m venv .venv
```

### 2. Activate the Environment

```bash
source .venv/bin/activate
```

### 3. Install Dependencies

Install the OMIM GeneMap2 parser and required libraries:

```bash
pip install git+https://github.com/azimgivron/genemap2-parser.git pandas
```

---

## 🧩 Data Processing Pipeline

### Step 1 — Parse Raw OMIM Data

Run the parser on the **OMIM GeneMap2** file:

```bash
parseGeneMap2 -i omim2018/raw/genemap2.txt -o .
```

This extracts gene and phenotype information and produces a serialized output file (e.g., `output.pickle`).

### Step 2 — Post-Process the Parsed Data

Filter and refine the parsed data:

```bash
python3 post.py
```

The post-processing is supposed to reproduce the steps in **Beegle** paper:
```
OMIM provides a list of disease–gene annotations (6377 annotations in July 2013) based on experimental evidence. The annotation list is a combination of disease–gene entries that contains both confirmed and non-confirmed entries, as well as different mapping evidence. Note that each entry has a list of gene symbols, which includes both official symbols and aliases. Furthermore, many OMIM entries refer to the same disease concept. We refine this list in five steps:

(i) We remove non-confirmed entries.
(ii) We keep only the annotations whose evidence is based on mutations that are located within genes.
(iii) We keep only official gene symbols.
(iv) We combine disease entries that refer to the same disease concept.
(v) We keep only disease entries that have at least three genes annotated.
```
*ElShal S, Tranchevent LC, Sifrim A, Ardeshirdavani A, Davis J, Moreau Y. Beegle: from literature mining to disease-gene discovery. Nucleic Acids Res. 2016 Jan 29;44(2):e18. doi: 10.1093/nar/gkv905. Epub 2015 Sep 17. PMID: 26384564; PMCID: PMC4737179.*