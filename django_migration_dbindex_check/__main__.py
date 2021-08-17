from .checker import DBIndexChecker
import sys, os

if __name__ == "__main__":
    checker = DBIndexChecker()

    if len(sys.argv) < 2:
        path = os.getcwd()
    else:
        path = sys.argv[1]
    if not os.path.isabs(path):
        path = os.path.join(os.getcwd(), path)
    if not os.path.exists(path):
        raise ValueError(f"{path} is not a valid path.")

    checker.check_project(path)
