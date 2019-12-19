from sys import argv
from os import mkdir
from shutil import copy
import json
import venv


with open("files_to_copy.json") as files_file:
    filelist = json.load(files_file)

path = argv[1]
if path[-1] != "/":
    path += "/"
try:
    mkdir(path)
except FileExistsError:
    pass

# make sure to set the correct verison of python
shell_script = """#!/bin/sh
bash venv/bin/activate
alias python=python3.8
python -m pip install requests irc
python settings.py
rm setup.sh""".format(path=path)

for file in filelist:
    copy(f"./{file}", path + file)

with open(path + "setup.sh", "w") as setup_sh:
    setup_sh.write(shell_script)

venv.create(path + "/venv", system_site_packages=True)
