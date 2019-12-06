timers = []

class Timer:
	def __init__(self, message="", cooldown=0):
		self.message = message
		self.cooldown = cooldown

timer = Timer()
timers.append(timer)