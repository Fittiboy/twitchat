"""Use these instances as placeholders to test commands.py"""


class E:
    def __init__(self):
        self.tags = [{'key': 'user-id', 'value': '1234TEST'}, {'key': 'badges',
                     'value': 'testbadge/1'}]


class C:
    def __init__(self):
        pass

    def privmsg(self, one, two):
        print(two)


class Bot:
    def __init__(self):
        self.channel = None


e = E()
c = C()
bot = Bot()
