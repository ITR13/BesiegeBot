simport subprocess
import time
import os

if __name__ == '__main__':
	path = os.path.dirname(os.path.realpath(__file__))
	print(path)
	while True:
		while True:
			subprocess.run(
				["git", "fetch", "--all"], 
				cwd=path
			)
			subprocess.run(
				["git", "reset", "--hard", "origin/master"], 
				cwd=path
			)
			result = subprocess.run(
				["python3.6", "sourcecube.py"], 
				cwd=path
			)
			if result.returncode != 0:
				break
		time.sleep(5 * 60)
