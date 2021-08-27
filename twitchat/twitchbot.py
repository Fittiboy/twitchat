import irc.bot
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

    def on_disconnect(self, c, e):
        """Attempts to reconnect, with increasing time waited in between
        attempts.
        """

        time.sleep(self.reconnect)
        self.reconnect *= 2
        c.reconnect()

    def on_pubmsg(self, c, e):
        """Tries to execute command if message begins with '!'.  Also handles
        the posting of timed messages and reformats some of the input.

        A special case is handled in which the !reload command is called.  This
        is only allowed for the broadcaster and has to be executed outside of
        commands.py.  The !reload commands reloads the commands.py module.

        Additionally, the unnatural format of e.tags is turned
        into a more reasonable dictionary, also containing a dictionary
        representation of the badges.
        """

        if e.arguments[0][0] == "!":
            # e.tags comes as a list of dictionaries of the form
            # {'key': key, 'value': value}.  This line changes that
            # to a single dictionary of the more reasonable form {key: value}.
            e.tags = {dct['key']: dct['value'] for dct in e.tags}
            badges_tag = e.tags.get('badges')
            badges_list = []
            # The badges come as a string with the format
            # 'badge/version,badge/version,badge/version...'.
            #
            # This code converts the string into a more natural
            # dictionary of the form {badge: version, ...}.
            if badges_tag:
                badges_list = badges_tag.split(",")
            badges_list_collection = [badge.split("/") for badge
                                      in badges_list if badge]

            badges = {badge_list[0]: badge_list[1] for badge_list
                      in badges_list_collection}
            # Update the badges tag for later use in commands.py
            e.tags['badges'] = badges
            # Reloads the commands.py module, allowing for modification of
            # existing commands while the bot is still running.
            if e.arguments[0] == "!reload":
                if badges.get('broadcaster') == '1':
                    global cmd_obj
                    global commands
                    commands = reload(commands)
                    cmd_obj = commands.Commands()
            else:
                self.exec_command(c, e, cmd_obj)

        else:
            # Times messages are only sent after a certain amount of non-timed
            # messages.  Calling send_timers from here allows counting
            # messages.  Timed messages should not follow execution of commands
            # immediately, so this is only called if no command was used.
            self.send_timers(self.timers(), c)

    @commands.exec
    def exec_command(self, c, e, cmd_obj):
        """Check if command exists and checks for cooldown, then exectues if
        permitted.
        """

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
