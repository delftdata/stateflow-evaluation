import matplotlib.pyplot as plt
from matplotlib import rcParams, rc
rcParams['figure.figsize'] = [5, 4]
x = [100, 200, 300, 400, 500, 600, 700]
y = [495.61, 579.07, 645.12, 645.12, 830.97, 1003, 1960]
y_aws = [1370, 3510, 8550, 8940, 10590, 13210, 12350]

# Without locking
y_aws_new = [136, 141, 110, 114, 120, 127, 148]

y_99 = [998.40, 1320, 1460, 1280, 1840, 3300, 15880]
y_99_aws = [11280, 18840, 28250, 27740, 33160, 34700, 33370]

# Without locking
y_99_aws_new = [303, 326, 232, 226, 221, 267, 294]
plt.grid(axis="y", linestyle="--")
plt.plot(x, y_aws_new, "-o", color="#118ab2", label="AWS Lambda 50p")
plt.plot(x, y_99_aws_new, "--", marker="^", color="#118ab2", label="AWS Lambda 99p")
plt.plot(x, y, "-o", color="#ef476f", label="Flink Statefun 50p")
plt.plot(x, y_99, "--", marker="^", color="#ef476f", label="Flink Statefun 99p")
plt.legend()
plt.ylabel("Latency (in ms)")
plt.xlabel("Throughput (req/s)")
plt.tight_layout()
plt.savefig("deathstar_throughput.pdf")
plt.show()
