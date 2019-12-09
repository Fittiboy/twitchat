import shelve

db = shelve.open('database')
tokens = db['tokens']
twitch = tokens['twitch']
twitch['channel'] = input("New channel: ")
tokens['twitch'] = twitch
db['tokens'] = tokens