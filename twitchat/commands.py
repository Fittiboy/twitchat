import functools
from datetime import datetime
import json

from twitchat.get_user_info import get_uid
from twitchat.duckduckgo_abstract import abstract

import extra_commands as ec


def exec(func):
    @functools.wraps(func)
    def exec_wrapper(*args, **kwargs):
        e, c, bot, cmd_obj = func(*args, **kwargs)
        msg = e.arguments[0].split(" ")
        e.arguments[0] = cmd_obj
        if len(msg[0]) == 1:
            return
        cmd = msg[0][1:]
        cmd_func_name = f"on_{cmd}".lower()
        method = getattr(cmd_obj, cmd_func_name, Commands.nothing)
        method(e, msg, c, bot)
    return exec_wrapper


class Commands:
    """Add all commands as methods to this class"""
    def __init__(self):
        self.cooldowns = {}
        for key, value in ec.__dict__.items():
            if len(key) > 3 and key[:3] == "on_":
                cd = ec.cooldowns[key]
                cooled = Commands.check_cooldown(cd)(value)
                permitted = Commands.check_permissions(cooled)
                self.__dict__[key] = permitted

    def nothing(self, *args):
        pass

    def check_cooldown(cooldown):
        """Use this decorator to add a cooldown to a command"""
        def cooldown_decorator(func):
            @functools.wraps(func)
            def cooldown_wrapper(*args, **kwargs):
                last_used = args[0].cooldowns.get(func.__name__)
                if last_used:
                    used_diff = datetime.now() - last_used
                    if used_diff.seconds < cooldown:
                        return
                args[0].cooldowns[func.__name__] = datetime.now()
                func(*args, **kwargs)
            return cooldown_wrapper
        return cooldown_decorator

    def check_permissions(func):
        """Use this decorator to add a permission check to a command"""
        @functools.wraps(func)
        def permissions_wrapper(*args, **kwargs):
            if len(args) == 4:
                args = list(args)
                args.insert(0, args[0].arguments[0])
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
                perms[func.__name__] = {
                    'all': "1",
                    'uids': [],
                    'badges': {},
                    'forbid': {
                        'all': "0",
                        'uids': [],
                        'badges': {}
                        }
                    }
                with open('permissions.json', 'w') as perms_file:
                    json.dump(perms, perms_file, indent=4)

            if func_perms:
                perm_uids = func_perms.get('uids')
                perm_badges = func_perms.get('badges')
                perm_all = func_perms.get('all')
                perm_forbid = func_perms.get('forbid')
                permitted = False
                forbidden = False
                if uid in perm_uids and uid not in perm_forbid['uids']:
                    permitted = True

                if uid in perm_forbid['uids']:
                    forbidden = True

                if perm_all == "1" and perm_forbid['all'] != "1":
                    permitted = True

                if perm_forbid['all'] == "1":
                    forbidden = True

                elif not forbidden:
                    for badge, value in badges.items():
                        if perm_badges.get(badge) == value:
                            permitted = True
                            break
                    for badge, value in badges.items():
                        if perm_forbid['badges'].get(badge) == value:
                            permitted = False
                            break

                if permitted and not forbidden:
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
    def on_channel(self, e, msg, c, bot):
        if len(msg) > 1:
            channel = msg[1]
            c.privmsg(bot.channel, f"Heading over to {channel}!")
            bot.channel = "#" + channel.lower()
            c.disconnect()
            bot.start()

    @check_permissions
    @check_cooldown(cooldown=0)
    def on_permissions(self, e, msg, c, bot):
        """Usage: !permissions add/remove/forbid command user/badge/all
        {username}/{badgename badge_value}
        you can check some possible badges at api.twitch.tv"""
        with open("permissions.json") as perms_file:
            perms = json.load(perms_file)

        if len(msg) >= 4:
            arf = msg[1]  # (a)dd (r)emove (f)orbid
            cmd = msg[2]  # (c)o(m)man(d)
            tp = msg[3]  # (t)y(p)e
        else:
            return

        cmd_perms = perms.get(f'on_{cmd}', None)

        if cmd_perms is None:
            cmd_perms = {
                'all': "0",
                'uids': [],
                'badges': {},
                'forbid': {
                    'all': "0",
                    'uids': [],
                    'badges': {}
                    }
                }

        if tp == "user" and len(msg) == 5:
            user = msg[4]

            try:
                uid = get_uid(bot.client_id, user)
            except Exception:
                return

            if arf == "add":
                if uid not in cmd_perms['uids']:
                    cmd_perms['uids'].append(uid)

                if uid in cmd_perms['forbid']['uids']:
                    cmd_perms['forbid']['uids'].remove(uid)

                c.privmsg(bot.channel, f"{user} can now use !{cmd}")

            elif arf == "remove":
                if uid in cmd_perms['uids']:
                    cmd_perms['uids'].remove(uid)

                c.privmsg(bot.channel, f"{user} can no longer use !{cmd}")

            elif arf == "forbid":
                if uid not in cmd_perms['forbid']['uids']:
                    cmd_perms['forbid']['uids'].append(uid)

                if uid in cmd_perms['uids']:
                    cmd_perms['uids'].remove(uid)

                c.privmsg(bot.channel, f"{user} is no longer allowed " +
                                       f"to use !{cmd}")

        elif tp == "badge" and len(msg) == 6:
            badge = msg[4]
            value = msg[5]

            if arf == "add":
                cmd_perms['badges'][badge] = value
                if cmd_perms['forbid']['badges'].get(badge) == value:
                    del cmd_perms['forbid']['badges'][badge]
                c.privmsg(bot.channel, f"Users with the {badge}/{value}" +
                                       f" badge can now use !{cmd}")

            elif arf == "remove":
                if cmd_perms['badges'].get(badge) == value:
                    del cmd_perms['badges'][badge]
                c.privmsg(bot.channel, f"Users with the {badge}/{value}" +
                                       f" badge can no longer use !{cmd}")

            elif arf == "forbid":
                cmd_perms['forbid']['badges'][badge] = value
                if cmd_perms['badges'].get(badge) == value:
                    del cmd_perms['badges'][badge]
                c.privmsg(bot.channel, f"Users with the {badge}/{value}" +
                                       " badge are not allowed to use " +
                                       f"!{cmd}")

        elif tp == "all":
            if arf == "add":
                cmd_perms['all'] = "1"
                cmd_perms['forbid']['all'] = "0"
                c.privmsg(bot.channel, "All users can now use" +
                                       f" !{cmd}")
            elif arf == "remove":
                cmd_perms['all'] = "0"
                c.privmsg(bot.channel, f"The !{cmd} command is no" +
                                       " longer available to all users")

            elif arf == "forbid":
                cmd_perms['forbid']['all'] = "1"
                cmd_perms['all'] = "0"
                c.privmsg(bot.channel, f"No user is allowed to use !{cmd}")

        perms[f'on_{cmd}'] = cmd_perms
        with open('permissions.json', 'w') as perms_file:
            json.dump(perms, perms_file, indent=4)
