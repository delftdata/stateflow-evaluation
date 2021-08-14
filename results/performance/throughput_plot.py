import matplotlib.pyplot as plt


x = [100, 200, 300, 400, 500, 600, 700]
y = [495.61, 579.07, 645.12, 645.12, 830.97, 1003, 1960]
y_aws = [1370, 3510, 8550, 8940, 10590, 13210, 12350]

y_99 = [998.40, 1320, 1460, 1280, 1840, 3300, 15880]
y_99_aws = [11280, 18840, 28250, 27740, 33160, 34700, 33370]

plt.plot(x, y, label="statefun 50p")
plt.plot(x, y_aws, label="aws 50p")
plt.plot(x, y_99, '--', color='tab:blue', label="statefun 99p")
plt.plot(x, y_99_aws, '--', color='tab:orange', label="aws 99p")
plt.legend()
#plt.ylim([0, 15000])
#plt.ylim([0, 2000])
plt.ylabel("Duration (in ms)")
plt.xlabel("Throughput (req/s)")
plt.show()