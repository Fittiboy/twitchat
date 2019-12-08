import functools

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

class Commands:
    def __init__(self):
        pass

    def do_nothing(*args, **kwargs):
        return None

    def on_ping(self, msg, c, bot):
        c.privmsg(bot.channel, 'pong')


commands = Commands()