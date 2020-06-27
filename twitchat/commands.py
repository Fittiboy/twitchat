import functools
from datetime import datetime
import json
from shutil import copyfile
import comm_template

from get_user_info import get_uid
from duckduckgo_abstract import abstract


def exec(func):
    @functools.wraps(func)
    def exec_wrapper(*args, **kwargs):
        e, c, bot, cmd_obj = func(*args, **kwargs)
        msg = e.arguments[0].split(" ")
        if len(msg[0]) == 1:
            return
        cmd = msg[0][1:]
        cmd_func_name = f"on_{cmd}".lower()
        method = getattr(cmd_obj, cmd_func_name, cmd_obj.extra)
        method(e, msg, c, bot)
    return exec_wrapper


class Commands:
    """Add all commands as methods to this class"""
    def __init__(self):
        self.cooldowns = {}

    def check_cooldown(cooldown):
        """Use this decorator to add a cooldown to a command"""
        def cooldown_decorator(func):
            @functools.wraps(func)
            def cooldown_wrapper(*args, **kwargs):
                last_used = args[0].cooldowns.get(func.__name__)
                if last_used:
                    used_diff = datetime.now() - last_used
                    if used_diff.seconds < cooldown:
                        self, e, msg, c, bot = args
                        cmd  = msg[0][1:]
                        current_cd = cooldown - used_diff.seconds
                        c.privmsg(bot.channel, f"{cmd} is still on" +
                                  f" a {current_cd} second cooldown!")
                        return
                args[0].cooldowns[func.__name__] = datetime.now()
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
                if uid in perm_uids and uid not in perm_forbid['uids']:
                    permitted = True

                if uid in perm_forbid['uids']:
                    permitted = False

                if perm_all == "1" and perm_forbid['all'] != "1":
                    permitted = True

                if perm_forbid['all'] == "1":
                    premitted = False

                elif permitted:
                    for badge, value in badges.items():
                        if perm_badges.get(badge) == value:
                            permitted = True
                            break
                    for badge, value in badges.items():
                        if perm_forbid['badges'].get(badge) == value:
                            permitted = False
                            break

                if permitted:
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
            except:
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
                                       f" badge are not allowed to use " +
                                       f"!{cmd}")

        elif tp == "all":
            if arf == "add":
                cmd_perms['all'] = "1"
                cmd_perms['forbid']['all'] = "0"
                c.privmsg(bot.channel, f"All users can now use" +
                                       f" !{cmd}")
            elif arf == "remove":
                cmd_perms['all'] = "0"
                c.privmsg(bot.channel, f"The !{cmd} command is no" +
                                       f" longer available to all users")

            elif arf == "forbid":
                cmd_perms['forbid']['all'] = "1"
                cmd_perms['all'] = "0"
                c.privmsg(bot.channel, f"No user is allowed to use !{cmd}")

        perms[f'on_{cmd}'] = cmd_perms
        with open('permissions.json', 'w') as perms_file:
            json.dump(perms, perms_file, indent=4)

    @check_permissions
    @check_cooldown(cooldown=0)
    def on_commadd(self, e, msg, c, bot):
        """!commadd command cooldown(not required, default 30) text(including {args})"""
        if len(msg) > 2:
            with open("commands_backups/num.json") as backupnum_file:
                backup_num = json.load(backupnum_file) + 1
            with open("commands_backups/num.json", "w") as backupnum_file:
                json.dump(backup_num, backupnum_file)
            path = "commands_backups/commands_{backup_num}.py"
            copyfile("commands.py", path)

            commname = msg[1][1:] if msg[1][0] == "!" else msg[1]

            try:
                cdwn = int(msg[2])
                if len(msg) > 3:
                    commtext = msg[3:]
                else:
                    commtext = ""
            except ValueError:
                cdwn = 30
                commtext = msg[2:]
            
            arguments = []

            for word in commtext:
                if "{" in word and "}" in word:
                    wordlist = word.replace("{", "}__ARGUMENT__").split("}")
                    for word in wordlist:
                        if "__ARGUMENT__" in word:
                            arguments.append(word[12:])

            commtext = " ".join(commtext)
            argnum = len(arguments)
            formatlist = []
            
            for index, arg in enumerate(arguments):
                msg_index = index + 1
                formatlist.append(f"{arg}=msg[{msg_index}]")
            if formatlist:
                formatstring = ".format(" + ", ".join(formatlist) + ")"
            else:
                formatstring = ""
            
            template = comm_template.template
            full_command = template.format(cdwn=cdwn, cmdname=commname,
                    argnum=argnum, text=commtext, formattext=formatstring)

            with open("commands.py") as commandsfile:
                lines = commandsfile.readlines()

            index = len(lines) - 2
            lines.insert(index, full_command)

            with open("commands.py", "w") as commandsfile:
                commandsfile.write("".join(lines))

    '''Add your custom commands below this comment, like this:
    @check_permissions
    @check_cooldown(cooldown=0)
    def on_testcomm(self, e, msg, c, bot):
        c.privmsg(bot.channel, "This is just a test command!")'''


