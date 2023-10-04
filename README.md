[![CI](https://github.com/bihealth/dotty/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/bihealth/dotty/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/bihealth/dotty/graph/badge.svg?token=eLNzGVw30U)](https://codecov.io/gh/bihealth/dotty)

# dotty - cdot-based position projection

## What can it do?

Run it the background, e.g., from `main` as

```
$ DATA_DIR=$PWD/data \
    pipenv run uvicorn dotty.main:app --host 0.0.0.0 --port 8080 --reload
```

Then, resolve c./n./g. variants to SPDI-like variants

```
$ curl 'http://127.0.0.1:8080/api/v1/to-spdi?q=NM_000059.3:c.274G%3EA' 2>/dev/null | jq .
{
  "spdi": {
    "assembly": "GRCh38",
    "contig": "13",
    "pos": 32319283,
    "reference_deleted": "C",
    "alternate_inserted": "A"
  }
}
```

## Obtaining Data

`datasets` is the NCBI `datasets` tool.

```
$ mkdir -p data
$ cd data

$ wget \
    https://github.com/SACGF/cdot/releases/download/v0.2.21/cdot-0.2.21.ensembl.grch37.json.gz \
    https://github.com/SACGF/cdot/releases/download/v0.2.21/cdot-0.2.21.ensembl.grch38.json.gz \
    https://github.com/SACGF/cdot/releases/download/v0.2.21/cdot-0.2.21.refseq.grch37.json.gz \
    https://github.com/SACGF/cdot/releases/download/v0.2.21/cdot-0.2.21.refseq.grch38.json.gz

$ download genome accession GCF_000001405.25 --filename GRCh37.zip
$ download genome accession GCF_000001405.40 --filename GRCh38.zip
$ unzip GRCh37.zip
$ unzip GRCh38.zip
$ seqrepo --root-directory $PWD load --namespace ncbi --instance-name seqrepo ncbi_dataset/data/GCF_000001405.*/*.fna
$ rm -rf GRCh3?.zip ncbi_dataset
```

## Terraform Project Management

```
$ export GITHUB_OWNER=bihealth
$ export GITHUB_TOKEN=ghp_<thetoken>

$ cd utils/terraform
$ terraform init
$ terraform import github_repository.dotty dotty
$ terraform validate
$ terraform fmt
$ terraform plan
$ terraform apply
```