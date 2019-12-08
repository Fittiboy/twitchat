import functools
from datetime import datetime

def exec(_commands):
    def exec_decorator(func):
        @functools.wraps(func)
        def exec_wrapper(*args, **kwargs):
            msg, c, bot = func(*args, **kwargs)
            if len(msg[0]) == 1:
                return
            cmd = msg[0][1:]
            cmd_func_name = f"on_{cmd}"
            method = getattr(_commands, cmd_func_name, _commands.do_nothing)
            method(msg, c, bot)
        return exec_wrapper
    return exec_decorator

# Add commands as methods
class Commands:
    def __init__(self):
        self.cooldowns = {}

    # Gets called when a command is not recognized
    def do_nothing(*args, **kwargs):
        return None

    # Use this decorator to add a cooldown to a command
    def update_cooldown(cooldown):
        def cooldown_decorator(func):
            @functools.wraps(func)
            def cooldown_wrapper(*args, **kwargs):
                last_used = commands.cooldowns.get(func.__name__)
                if last_used:
                    used_diff = datetime.now() - last_used
                    if used_diff.seconds < cooldown:
                        return
                commands.cooldowns[func.__name__] = datetime.now()
                func(*args, **kwargs)
            return cooldown_wrapper
        return cooldown_decorator

    # Not to confuse with the IRC ping event
    def on_ping(self, msg, c, bot):
        c.privmsg(bot.channel, 'pong')

    @update_cooldown(cooldown=30)
    def on_raid(self, msg, c, bot):
        print("raid")


commands = Commands()