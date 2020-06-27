import json
from twitchat import permissions


def main():
    try:
        with open('settings.json') as settings_file:
            settings = json.load(settings_file)
    except FileNotFoundError:
        settings = {}

    try:
        with open('permissions.json') as permissions_file:
            pass
    except FileNotFoundError:
        with open('permissions.json', 'w') as permissions_file:
            json.dump(permissions, permissions_file, indent=4)

    settings['username'] = input("Username: ")
    settings['client_id'] = input("Client-ID: ")
    settings['token'] = input("token: ")
    settings['channel'] = input("channel: ")
    settings['keepalive'] = 300
    with open('settings.json', 'w') as settings_file:
        json.dump(settings, settings_file, indent=4)
