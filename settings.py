import json

with open('settings.json') as settings_file:
    settings = json.load(settings_file)
settings['username'] = input("Username: ")
settings['client_id'] = input("Client-ID: ")
settings['token'] = input("token: ")
settings['channel'] = input("channel: ")
settings['keepalive'] = int(input("Keepalive (in seconds): "))
with open('settings.json', 'w') as settings_file:
    json.dump(settings, settings_file, indent=4)
