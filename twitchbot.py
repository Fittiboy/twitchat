import sys
import irc.bot
import requests
import asyncio
import _timers

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        r = requests.get(url, headers=self.headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)], username, username)

    async def _timer(self, timers):
        for timer in timers:
            pass

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)

    def on_reconnect(self, c, e):
        c.reconnect()

    def on_pubmsg(self, c, e):
        if e.arguments[0][0] == "!":
            self.exec_command(c, e)

    def exec_command(self, c, e):
        url = 'https://api.twitch.tv/kraken/channel/' + self.channel_id
        r = requests.get(url, headers=self.headers).json()

def main():
    username = sys.argv[1]
    client_id = sys.argv[2]
    token =  sys.argv[3]
    channel = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot._timer(_timers.timers)
    bot.start()

if __name__ == "__main__":
    main()
