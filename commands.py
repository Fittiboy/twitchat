import functools
from datetime import datetime
import shelve
from get_user_info import get_uid

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

    # Use this decorator to add permissions to a command
    def check_permissions(func):
        @functools.wraps(func)
        def permissions_wrapper(*args, **kwargs):
            uid = [dict['value'] for dict in args[1].tags if dict['key'] == 'user-id'][0]
            badges_tag = [dict['value'] for dict in args[1].tags if dict['key'] == 'badges']
            badges_list = badges_tag[0].split(",")
            badges_lists_list = [badge.split("/") for badge in badges_list]

            badges = {badge_list[0]:badge_list[1] for badge_list in badges_lists_list}

            db = shelve.open('database')
            perms = db['permissions']
            perm_uids = perms[func.__name__]['uids']
            perm_badges = perms[func.__name__]['badges']
            db.close()
            permitted = False
            if uid in perm_uids:
                permitted = True
            else:
                for badge, value in badges.items():
                    if perm_badges.get(badge, "not_permitted") == value:
                        permitted = True

            if permitted == True:
                func(*args, **kwargs)
        return permissions_wrapper


    # Not to confuse with the IRC ping event
    def on_ping(self, e, msg, c, bot):
        c.privmsg(bot.channel, 'pong')

    @check_permissions
    @update_cooldown(cooldown=30)
    def on_raid(self, e, msg, c, bot):
        print("raid")

    @check_permissions
    def on_permissions(self, e, msg, c, bot):
        """Usage: !permissions add/remove command user/badge
        {username}/{badgename} {badge_value}
        you can check the badges at api.twitch.tv"""
        db = shelve.open('database')
        perms = db['permissions']
        if len(msg) >= 4:
            aor = msg[1]
            cmd = msg[2]
            tp = msg[3]
        else:
            return
        cmd_perms = perms.get(f'on_{cmd}', None)
        if cmd_perms == None:
            newperms = {'uids': [], 'badges': {}}
            cmd_perms = newperms
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
                c.privmsg(bot.channel, f"Users with the {badge}/{value} badge can \
                    now use !{cmd}")
            if aor == "remove":
                if cmd_perms['badges'].get(badge) == value:
                    del cmd_perms['badges'][badge]
                c.privmsg(bot.channel, f"Users with the {badge}/{value} badge can \
                    no longer use !{cmd}")
        perms[f'on_{cmd}'] = cmd_perms
        db['permissions'] = perms
        db.close()


    '''A test function for you to check
    if your bot works. Remember to add
    your user-id to the dictionary in
    permissions.py'''
    @check_permissions
    @update_cooldown(cooldown=3)
    def on_test(self, e, msg, c, bot):
        c.privmsg(bot.channel, 'passed')


commands = Commands()