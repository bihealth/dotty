[![CI](https://github.com/bihealth/dotty/actions/workflows/main.yml/badge.svg?branch=main)](https://github.com/bihealth/dotty/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/bihealth/dotty/graph/badge.svg?token=HIBwaG4eYM)](https://codecov.io/gh/bihealth/dotty)

# dotty - cdot-based position projection

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