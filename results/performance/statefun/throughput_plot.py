import matplotlib.pyplot as plt


x = [100, 200, 300, 400, 500, 600, 700]
y = [495.61, 579.07, 645.12, 645.12, 830.97, 1003, 1960]

y_99 = [998.40, 1320, 1460, 1280, 1840, 3300, 15880]
plt.plot(x, y, label="statefun 50p")
plt.plot(x, y_99, label="statefun 99p")
plt.legend()
plt.ylim([0, 15000])
#plt.ylim([0, 2000])
plt.ylabel("Duration (in ms)")
plt.xlabel("Throughput (req/s)")
plt.show()