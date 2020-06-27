import json

try:
    with open('timers.json') as timerfile:
        timers = json.load(timerfile)
except FileNotFoundError:
    timers = {}
