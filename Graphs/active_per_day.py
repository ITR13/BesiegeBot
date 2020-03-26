from wisdom import *
from datetime import timedelta
from matplotlib import pyplot as plt
from tqdm import tqdm

start_range = datetime(2018, 12, 15, 0, 0, 0)
end_range = datetime(2020, 2, 17, 23, 0, 0)

total = (end_range - start_range)//timedelta(hours=1)


y = []
x = []
for end in tqdm(range(total + 1)):
	start_range = start_range + timedelta(hours=1)
	start = start_range - timedelta(days=1)
	end = start_range
	
	x.append(start_range)
	y.append(generate_message_count(2, start, end))

plt.plot(x, y)
plt.show()
