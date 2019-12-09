import shelve

db = shelve.open('database')
tokens = db['tokens']
twitch = tokens['twitch']
twitch['username'] = input("Username: ")
twitch['client_id'] = input("Client-ID: ")
twitch['token'] = input("token: ")
twitch['channel'] = input("channel: ")
twitch['keepalive'] = int(input("Keepalive (in seconds): "))
tokens['twitch'] = twitch
db['tokens'] = tokens
db.close()