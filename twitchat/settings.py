import json
from twitchat.permissions import permissions


def main():
    try:
        with open('settings.json') as settings_file:
            settings = json.load(settings_file)
    except FileNotFoundError:
        settings = {}

    try:
        open('timers.json').close()
    except FileNotFoundError:
        with open('timers.json', 'w') as timers_file:
            json.dump({}, timers_file, indent=4)

    try:
        open('extra_commands.py').close()
    except FileNotFoundError:
        open('extra_commands.py', 'w').close()

    try:
        open('permissions.json').close()
    except FileNotFoundError:
        with open('permissions.json', 'w') as permissions_file:
            json.dump(permissions, permissions_file, indent=4)

    set_setting(settings, 'username', 'Username: ')
    set_setting(settings, 'client_id', 'Client-ID: ')
    set_setting(settings, 'token', 'Token: ')
    set_setting(settings, 'channel', 'Channel: ')
    settings['keepalive'] = 300
    with open('settings.json', 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)


def set_setting(settings, setting, prompt):
    choice = input(prompt)
    if not choice:
        print("You have not entered a value. " +
              "If you want to leave this blank, " +
              "just hit enter again")
    if setting == "channel":
        choice = choice.lower()
    settings[setting] = choice
