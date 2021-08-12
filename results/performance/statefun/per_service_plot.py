import matplotlib.pyplot as plt


x = ["login", "search", "reserve", "recommend"]
y = [126.18333333333,  623.61333333333, 172.15666666667, 332.2]
y_err = [0.16679994670929,  12.746755555556, 1.8244694814901, 2.050609665441]

plt.bar(x, y, yerr=y_err, label="statefun", capsize=4)
plt.legend()
plt.ylabel("Duration (in ms)")
plt.xlabel("Endpoint")
plt.show()