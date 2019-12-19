from sys import argv
from os import mkdir
from shutil import copy
import json
import venv
from subprocess import call

with open("files_to_copy.json") as files_file:
    filelist = json.load(files_file)

path = argv[1]
if path[-1] != "/":
    path += "/"
try:
    mkdir(path)
except FileExistsError:
    pass

shell_script = """#!/bin/sh
bash venv/bin/activate
python3 -m pip install requests irc
python3 settings.py
rm setup.sh""".format(path=path)

for file in filelist:
    copy(f"./{file}", path + file)

with open(path + "setup.sh", "w") as setup_sh:
    setup_sh.write(shell_script)

venv.create(path + "/venv", system_site_packages=True)
