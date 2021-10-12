import matplotlib.pyplot as plt
from matplotlib import rcParams, rc
rcParams['figure.figsize'] = [6, 5]
# x = [100, 200, 300, 400, 500, 600, 700]
x = [620, 1240, 1860, 2480, 3100, 3720, 4340]
y = [495.61, 579.07, 645.12, 645.12, 830.97, 1003, 1960]
y_aws = [1370, 3510, 8550, 8940, 10590, 13210, 12350]
y_flink = [398.85, 442.62, 496.64, 597.50, 653.31, 709.12, 762.37]

# Without locking
y_aws_new = [136, 141, 110, 114, 120, 127, 148]

y_99 = [998.40, 1320, 1460, 1280, 1840, 3300, 15880]
y_99_aws = [11280, 18840, 28250, 27740, 33160, 34700, 33370]
y_99_flink = [744.45, 826.37, 937.98, 1009, 1350, 1430, 1680]

# Without locking
y_99_aws_new = [303, 326, 232, 226, 221, 267, 294]

plt.grid(axis="y", linestyle="--")
plt.plot(x, y_aws_new, "-o", color="#118ab2", label="AWS Lambda 50p")
plt.plot(x, y_99_aws_new, "--", marker="^", color="#118ab2", label="AWS Lambda 99p")
plt.plot(x, y, "-o", color="#ef476f", label="Flink Statefun 50p")
plt.plot(x, y_99, "--", marker="^", color="#ef476f", label="Flink Statefun 99p")
plt.plot(x, y_flink, "-o", color="#06d6a0", label="Flink + AWS 50p")
plt.plot(x, y_99_flink, "--", marker="^", color="#06d6a0", label="Flink + AWS 99p")
plt.legend()
#plt.annotate("15880 ms", xy=(700, 4000,), xytext=(700, 4100), color="black", ha="center", arrowprops=dict(arrowstyle='<-',lw=1.2))
plt.ylim([0, 2200])
plt.ylabel("Latency (in ms)")
plt.xlabel("Throughput (req/s)")
plt.tight_layout()
plt.savefig("deathstar_throughput.pdf")
plt.show()
