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

for file in filelist:
    copy(f"./{file}", path + file)

venv.create(path + "/venv", system_site_packages=True, with_pip=True)

print("Make sure to run 'python -m pip install requests irc' in your venv\n" +
      "To set up your bot, run settings.py")
