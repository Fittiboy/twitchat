Adding your own Commands
^^^^^^^^^^^^^^^^^^^^^^^^

To add your own commands, you need to add them to ``extra_commands.py``, a file that will be created after running ``twitchat-setting`` (refer to `Quick start`_).

The general template for your commands will be:::
    
    def on_command_name(self, e, msg, c, bot):
        c.privmsg(bot.channel, "This is what the bot will say") 

Additionally, in the same file, you will need to have a dictionary with the cooldowns for each command:::

    cooldowns = {
                  'on_comm1': 10,
                  'on_comm2': 2,
                  'on_comm3': 0
    }

In this case, the !comm2 command will have a 2 second cooldown, the !comm1 command a 10 second cooldown, and the !comm3 command (you guessed it) no cooldown at all.

.. _Quick start: quickstart.html

