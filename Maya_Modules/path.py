# coding: utf-8
import os


def showPath():
    paths = os.environ["MAYA_SCRIPT_PATH"]
    for path in paths.split(";"):
        print(path)





