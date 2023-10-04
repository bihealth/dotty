[![CI](https://github.com/bihealth/dotty/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/bihealth/dotty/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/bihealth/dotty/graph/badge.svg?token=eLNzGVw30U)](https://codecov.io/gh/bihealth/dotty)

# dotty - cdot-based position projection

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