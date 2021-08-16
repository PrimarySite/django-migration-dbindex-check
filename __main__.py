from django_migration_dbindex_check.checker import DBIndexChecker
import sys

if __name__ == '__main__':
    checker = DBIndexChecker()
    checker.check_project(sys.argv[0])
