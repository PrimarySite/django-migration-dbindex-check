# Django-migration-dbindex-checker
[![CircleCI](https://circleci.com/gh/PrimarySite/django-migration-dbindex-check/tree/master.svg?style=svg)](https://circleci.com/gh/PrimarySite/django-migration-dbindex-check/tree/master)
[![codecov](https://codecov.io/gh/PrimarySite/django-migration-dbindex-check/branch/master/graph/badge.svg?token=DBL4fCqCQq)](https://codecov.io/gh/PrimarySite/django-migration-dbindex-check)

Automatically check your Django migrations for a new db_index=True

This package checks your Django project for any migrations 
that have new database indices and lets you know where they are. 
It's designed to be implemented ad a CI check warning you before you deploy.


##Why do I need this?
The default behaviour of most SQL databases when creating a new index is to lock 
the specified table and scan each row sequentially to create the index.
On existing projects with large databases this can take some time and will cause downtime 
on your production application. This check will warn you so you can migrate out of hours, 
use Postgres' CONCURRENTLY feature or schedule downtime.


##Installation
Install from pypi - `pip install django-migration-db-index-checker`

Install from git repo - `pip install -e git+https://github.com/JakeLSaunders94/django-migration-dbindex-check.git#egg=django-migration-dbindex-check`


##Usage
The package is designed to be used from the command line: 
1. Navigate to your projects root folder.
2. python -m django-migration-db-index-checker

or 

1. python -m django-migration-db-index-checker <your_root_path>

The script will then output a list of offending migrations as per this example:
