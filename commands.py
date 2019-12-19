import functools
from datetime import datetime
import json

from get_user_info import get_uid
from duckduckgo_abstract import abstract


def exec(_commands):
    def exec_decorator(func):
        @functools.wraps(func)
        def exec_wrapper(*args, **kwargs):
            e, c, bot = func(*args, **kwargs)
            msg = e.arguments[0].split(" ")
            if len(msg[0]) == 1:
                return
            cmd = msg[0][1:]
            cmd_func_name = f"on_{cmd}"
            method = getattr(_commands, cmd_func_name, _commands.do_nothing)
            method(e, msg, c, bot)
        return exec_wrapper
    return exec_decorator


class Commands:
    """Add all commands as methods to this class"""
    def __init__(self):
        self.cooldowns = {}

    def do_nothing(*args, **kwargs):
        """Gets called when a command is not recognized"""
        pass

    def check_cooldown(cooldown):
        """Use this decorator to add a cooldown to a command"""
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

    def check_permissions(func):
        """Use this decorator to add a permission check to a command"""
        @functools.wraps(func)
        def permissions_wrapper(*args, **kwargs):
            uid = [dict['value'] for dict in args[1].tags
                   if dict['key'] == 'user-id'][0]
            badges_tag = [dict['value'] for dict in args[1].tags
                          if dict['key'] == 'badges']
            badges_list = []
            if badges_tag[0]:
                badges_list = badges_tag[0].split(",")
            badges_lists_list = [badge.split("/") for badge in badges_list
                                 if badge]

            badges = {badge_list[0]: badge_list[1] for badge_list
                      in badges_lists_list}

            with open('permissions.json') as perms_file:
                perms = json.load(perms_file)
            func_perms = perms.get(func.__name__)

            if not func_perms:
                perms[func.__name__] = {'all': "1", 'uids': [], 'badges': {}}
                with open('permissions.json', 'w') as perms_file:
                    json.dump(perms, perms_file)

            if func_perms:
                perm_uids = func_perms.get('uids')
                perm_badges = func_perms.get('badges')
                perm_all = func_perms.get('all')
                permitted = False
                if uid in perm_uids or perm_all == "1":
                    permitted = True
                else:
                    for badge, value in badges.items():
                        if perm_badges.get(badge, "not_permitted") == value:
                            permitted = True

                if permitted is True:
                    func(*args, **kwargs)

        return permissions_wrapper

    # STOCK COMMANDS
    @check_permissions
    @check_cooldown(cooldown=0)
    def on_ping(self, e, msg, c, bot):
        """Checks if the bot is alive"""
        c.privmsg(bot.channel, 'pong')

    @check_permissions
    @check_cooldown(cooldown=10)
    def on_abstract(self, e, msg, c, bot):
        """Tries to find basic information on search term
        using the duckduckgo.com search engine"""
        if len(msg) > 1:
            term = " ".join(msg[1:])
            c.privmsg(bot.channel, abstract(term))

    @check_permissions
    @check_cooldown(cooldown=0)
    def on_permissions(self, e, msg, c, bot):
        """Usage: !permissions add/remove command user/badge/all
        {username}/{badgename badge_value}
        you can check some possible badges at api.twitch.tv"""
        with open("permissions.json") as perms_file:
            perms = json.load(perms_file)

        if len(msg) >= 4:
            aor = msg[1]  # (a)dd (o)r (r)emove
            cmd = msg[2]  # (c)o(m)man(d)
            tp = msg[3]  # (t)y(p)e
        else:
            return

        cmd_perms = perms.get(f'on_{cmd}', None)

        if cmd_perms is None:
            cmd_perms = {'all': "0", 'uids': [], 'badges': {}}

        if tp == "user" and len(msg) == 5:
            user = msg[4]
            uid = get_uid(bot.client_id, user)
            if aor == "add":
                if uid not in cmd_perms['uids']:
                    cmd_perms['uids'].append(uid)
                c.privmsg(bot.channel, f"{user} can now use !{cmd}")
            elif aor == "remove":
                if uid in cmd_perms['uids']:
                    cmd_perms['uids'].remove(uid)
                c.privmsg(bot.channel, f"{user} can no longer use !{cmd}")
        elif tp == "badge" and len(msg) == 6:
            badge = msg[4]
            value = msg[5]
            if aor == "add":
                cmd_perms['badges'][badge] = value
                c.privmsg(bot.channel, f"Users with the {badge}/{value}" +
                                       f" badge can now use !{cmd}")
            elif aor == "remove":
                if cmd_perms['badges'].get(badge) == value:
                    del cmd_perms['badges'][badge]
                c.privmsg(bot.channel, f"Users with the {badge}/{value}" +
                                       f" badge can no longer use !{cmd}")
        elif tp == "all":
            if aor == "add":
                cmd_perms['all'] = "1"
                c.privmsg(bot.channel, f"All users can now use" +
                                       f" !{cmd}")
            elif aor == "remove":
                cmd_perms['all'] = "0"
                c.privmsg(bot.channel, f"The !{cmd} command is no" +
                                       f" longer available to all users")

        perms[f'on_{cmd}'] = cmd_perms
        with open('permissions.json', 'w') as perms_file:
            json.dump(perms, perms_file)

    '''Add your custom commands below this comment, like this:
    @check_permissions
    @check_cooldown(cooldown=0)
    def on_testcomm(self, e, msg, c, bot):
        c.privmsg(bot.channel, "This is just a test command!")'''


commands = Commands()
