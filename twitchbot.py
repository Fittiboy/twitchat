import irc.bot
import requests
import time
import commands
import shelve

class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel, keepalive=30):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel
        self.headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        self.keepalive = keepalive
        self.reconnect = 1 # double every failed reconnection attmept

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        r = requests.get(url, headers=self.headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:'+token)],\
        	username, username)

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        c.join(self.channel)
        c.set_keepalive(self.keepalive)
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
            self.exec_command(c, e)

    @commands.exec(commands.commands)
    def exec_command(self, c, e):
        """Check if command exists and checks for possible cooldown,
        then executes if possible"""
        return e, c, self

def main():
    db = shelve.open('database')
    tkns = db['tokens']['twitch']
    username = tkns['username']
    client_id = tkns['client_id']
    token =  tkns['token']
    channel = tkns['channel']
    keepalive = tkns['keepalive']
    db.close()

    bot = TwitchBot(username, client_id, token, channel, keepalive)
    bot.start()

if __name__ == "__main__":
    main()
