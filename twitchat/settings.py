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

    settings['username'] = input("Username: ")
    settings['client_id'] = input("Client-ID: ")
    settings['token'] = input("token: ")
    settings['channel'] = input("channel: ").lower()
    settings['keepalive'] = 300
    with open('settings.json', 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)
