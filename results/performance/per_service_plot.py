import matplotlib.pyplot as plt
import numpy as np

labels = ["login", "search", "reserve", "recommend"]
statefun_means = [126.18333333333,  623.61333333333, 172.15666666667, 332.2]
statefun_err = [0.16679994670929,  12.746755555556, 1.8244694814901, 2.050609665441]

aws_means = [74.05,  	293.46333333333,73.643333333333, 130.28]
aws_err = [0.15513435037627,  9.7107683641524, 1.5979222620502, 7.4055429690649]

x = np.arange(len(labels))  # the label locations
width = 0.35  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, statefun_means, width, label='statefun', yerr=statefun_err, capsize=4)
rects2 = ax.bar(x + width/2, aws_means, width, label='aws', yerr=aws_err, capsize=4)

plt.legend()
ax.set_ylabel('Latency (in ms)')
ax.set_xticks(x)
ax.set_xticklabels(labels)
plt.xlabel("Endpoint")
ax.legend()

fig.tight_layout()
plt.show()