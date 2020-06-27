# Python Twitch Bot
## (Q: What is a "python"??)
A: Go to [python.org](https://www.python.org/downloads) and download and install the latest version of python.<br>

During installation, where it gives you the option to "include in PATH", tick the box! This allows you to run python by just typing `python` in a console window (just type Command Prompt or Windows PowerShell into your Windows search bar if you're using Windows, look for your Terminal on Mac and Linux).<br>

You just installed an interpreter that translates from python to a language your computer speaks. This will be used to run the bot.<br>

Don't worry, it's two lines of code that you can just copy and paste!<br>

P.S.: When I tell you to "run something in a directory" (directory = folder), it means you should run that command in your Terminal after navigating to that directory.<br>
To navigate to a directory in a terminal, use the `cd path/to/directory` command, where "path/to/directory" is replaced by wherever you wanna go (for example "C:\Users". When you're already in C:\\, you can just type `cd Users`).<br>
The cd command works on Windows, Mac and Linux.

## Quick setup
To get the bot up and running immediately, you have to do the following:
1. `pip install twitchat` (or `python -m pip install twitchat` if that doesn't work for you)
2. Create a directory for the bot
3. Inside this directory, run `twitchat-settings`

Here, you will have to enter the following:
1. The name of your bot account
2. A client ID for that account
3. A corresponding oauth token (This can easily be acquired from [here](https://twitchapps.com/tmi); exclude the "oauth:" part)
4. The channel you want the bot to connect to

If you don't know what any of this means, I have a [guide](https://github.com/Fittiboy/python-twitch-bot#how-to-set-up-your-bot-account) prepared for you.

Finally, create a script in the bot directory (or just run python):<br>
```python
from twitchat.twitchbot import main
main()
```
Your bot should now be connecting to your Twitch chat and saying "I am here now :)". Try using !ping to see him reply!<br>

Refer to the [full documentation](https://python-twitch-bot.readthedocs.io/en/latest/index.html) for further configuration of your bot, including all your commands.

## How to set up your bot account

If you don't have a bot account yet, go ahead and [create](https://www.twitch.tv/signup) one right now.<br>
Before doing so, you may also go to your [settings](https://www.twitch.tv/settings/security) and "Enable additional account creation"
![Enable additional account creation](https://i.imgur.com/22XLyDQ.png)<br>
When you're done, head over to Twitch's [developer website](https://dev.twitch.tv/) and hit "Log in with Twitch" on the top right.<br>
In your [dashboard](https://dev.twitch.tv/console/apps)'s "Applications" tab, you hit the "Register Your Applicatoin" button on the right.<br>
Put whatever you want into the "Name" field, and put "https://localhost" into the "OAuth Redirect URLs" field, since these fields are not strictly relevant for us.<br>
Finally, you chose "Chat Bot" as the category and hit "Create".<br>
You will now see your chat bot in the list of Applications, where you click "Manage".
![Chat bot application](https://i.imgur.com/QPnkso3.png)<br>
Here you will see that here is a new field called "Client ID", which you will need in the next step. __Keep this secret!__<br>
For the final step, head over to [this site](https://twitchapps.com/tmi) and connect it to your Twitch bot account to obtain your oauth token (remove the "oauth:" part).

## Full documentation

The full documentation for the bot is available [here](https://python-twitch-bot.readthedocs.io/en/latest/index.html)
