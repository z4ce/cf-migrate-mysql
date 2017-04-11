## Synopsis
A quick and dirty script that creates services and service keys and dumps/loads mysql databases in cloudfoundry.

## Prerequisites

* cf cli in path
* mysql in path
* mysqldump in path

mysqldump should be at least version 5.5 so that it will insert no foreign key check statements.

## Usage
```
usage: cf-migrate-mysql.py [-h] --src-api SRC_API --src-user SRC_USER
                           --src-pass SRC_PASS --src-org SRC_ORG --src-space
                           SRC_SPACE --dst-api DST_API --dst-user DST_USER
                           --dst-pass DST_PASS --dst-org DST_ORG --dst-space
                           DST_SPACE

Moves MySQL from one space to another including creating services. Service
plans must be the same between environments.

optional arguments:
  -h, --help            show this help message and exit
  --src-api SRC_API     URL for source API
  --src-user SRC_USER   username for source API
  --src-pass SRC_PASS   password for source API
  --src-org SRC_ORG     org name for source
  --src-space SRC_SPACE
                        space name for source
  --dst-api DST_API     URL for destination API
  --dst-user DST_USER   username for destination API
  --dst-pass DST_PASS   password for destination API
  --dst-org DST_ORG     org name for destination
  --dst-space DST_SPACE
                        space name for destination
```
