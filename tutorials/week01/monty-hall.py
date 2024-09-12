import random

reps = 10^9

def run(switch: bool, reps: int = 100):
	wins = 0

	for r in range(reps):
		wdoor = random.randint(1, 3)
		cdoor = random.randint(1, 3)

		if switch:
			rdoors = [1, 2, 3]
			rdoors.remove(cdoor)
			cdoor = rdoors[random.randint(0,1)]

		if cdoor == wdoor:
			wins += 1
	return wins

if run(False, reps) < run(True, reps):
	print("Is better.")
else:
	print("Is worse.")