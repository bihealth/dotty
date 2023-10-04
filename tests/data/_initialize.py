"""Helper script to initialize the data from downloads.

Will extract records from BRCA1 / ENSG00000012048 / NCBI_GENE_ID:672

Preparation steps:

::

    mkdir -p /tmp/data
    cd /data

    wget \
        https://github.com/SACGF/cdot/releases/download/v0.2.21/cdot-0.2.21.ensembl.grch37.json.gz \
        https://github.com/SACGF/cdot/releases/download/v0.2.21/cdot-0.2.21.ensembl.grch38.json.gz \
        https://github.com/SACGF/cdot/releases/download/v0.2.21/cdot-0.2.21.refseq.grch37.json.gz \
        https://github.com/SACGF/cdot/releases/download/v0.2.21/cdot-0.2.21.refseq.grch38.json.gz

    cd path/to/test/data
    CDOT_DIR=/tmp/data python3 _initialize.py
"""

import gzip
import json
import os

CDOT_DIR = os.environ["CDOT_DIR"]

for fname in ("cdot-0.2.21.ensembl.grch37.json.gz", "cdot-0.2.21.ensembl.grch38.json.gz"):
    with gzip.open(f"{CDOT_DIR}/{fname}", "rt") as f:
        ensembl = json.load(f)
    ensembl["genes"] = {
        k: v for k, v in ensembl["genes"].items() if k.startswith("ENSG00000012048")
    }
    ensembl["transcripts"] = {
        k: v for k, v in ensembl["transcripts"].items() if v["gene_version"] == "ENSG00000012048"
    }
    with gzip.open(fname, "wt") as f:
        json.dump(ensembl, f, indent=2)


for fname in ("cdot-0.2.21.refseq.grch37.json.gz", "cdot-0.2.21.refseq.grch38.json.gz"):
    with gzip.open(f"{CDOT_DIR}/{fname}", "rt") as f:
        ensembl = json.load(f)
    ensembl["genes"] = {k: v for k, v in ensembl["genes"].items() if k == "672"}
    ensembl["transcripts"] = {
        k: v for k, v in ensembl["transcripts"].items() if v["gene_version"] == "672"
    }
    with gzip.open(fname, "wt") as f:
        json.dump(ensembl, f, indent=2)
