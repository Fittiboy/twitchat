import irc.bot
import requests
import time
from time import time as nowfunc
import twitchat.commands as commands
import json
from importlib import reload


cmd_obj = commands.Commands()


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel, keepalive=30):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.headers = {'Client-ID': client_id,
                        'Accept': 'application/vnd.twitchtv.v5+json'}
        self.keepalive = keepalive
        self.reconnect = 1  # double every failed reconnection attmept

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        r = requests.get(url, headers=self.headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(
                self, [(server, port, 'oauth:'+token)],
                username, username)

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        c.set_keepalive(self.keepalive)
        c.privmsg(self.channel, "I am here now :)")
        self.reconnect = 1

    def on_reconnect(self, c, e):
        time.sleep(self.reconnect)
        self.reconnect *= 2
        c.reconnect()

    def on_disconnect(self, c, e):
        time.sleep(self.reconnect)
        self.reconnect *= 2
        c.reconnect()

    def on_dccdisconnect(self, c, e):
        time.sleep(self.reconnect)
        self.reconnect *= 2
        c.reconnect()

    def on_pubmsg(self, c, e):
        """Tries to execute command if message begins with '!'"""
        if e.arguments[0][0] == "!":
            global cmd_obj
            if e.arguments[0] == "!reload":
                badges_tag = [dict['value'] for dict in e.tags
                              if dict['key'] == 'badges']
                badges_list = []
                if badges_tag[0]:
                    badges_list = badges_tag[0].split(",")
                badges_lists_list = [badge.split("/") for badge in badges_list
                                     if badge]

                badges = {badge_list[0]: badge_list[1] for badge_list
                          in badges_lists_list}
                for badge, value in badges.items():
                    if badge == "broadcaster" and value == "1":
                        global commands
                        commands = reload(commands)
                        cmd_obj = commands.Commands()
            else:
                self.exec_command(c, e, cmd_obj)

        else:
            self.send_timers(self.timers(), c)

    @commands.exec
    def exec_command(self, c, e, cmd_obj):
        """Check if command exists and checks for possible cooldown,
        then executes if possible"""
        return e, c, self, cmd_obj

    def timers(self):
        now = nowfunc()
        send = []
        with open('timers.json') as timerfile:
            timers = json.load(timerfile)

        for command, params in timers.items():
            params['messages'] += 1
            messages = params['messages']
            messages_threshold = params['messages_threshold']

            time = params['time']
            time_threshold = params['time_threshold']
            if (now - time > time_threshold and
               messages > messages_threshold):
                params['messages'] = 0
                params['time'] = now
                send.append(command)

            timers[command] = params

        with open('timers.json.bak', 'w') as timerbackup:
            json.dump(timers, timerbackup, indent=4)

        with open('timers.json', 'w') as timerfile:
            json.dump(timers, timerfile, indent=4)

        return send

    def send_timers(self, send, c):
        with open('timers.json') as timerfile:
            timers = json.load(timerfile)
        for command in send:
            name = timers[command]
            c.privmsg(self.channel,
                      name['post'])


def main():
    with open('settings.json') as settings_file:
        settings = json.load(settings_file)
    username = settings['username']
    client_id = settings['client_id']
    token = settings['token']
    channel = settings['channel']
    keepalive = settings['keepalive']

    bot = TwitchBot(username, client_id, token, channel, keepalive)
    bot.start()
