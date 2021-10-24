import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams, rc
rcParams['figure.figsize'] = [8, 4]
labels = ["login", "search", "reserve", "recommend"]
statefun_means = [126.18333333333, 623.61333333333, 172.15666666667, 332.2]
statefun_err = [0.16679994670929, 12.746755555556, 1.8244694814901, 2.050609665441]

aws_means = [74.05, 293.46333333333, 73.643333333333, 130.28]
aws_err = [0.15513435037627, 9.7107683641524, 1.5979222620502, 7.4055429690649]

aws_no_lock_means = [35.613333333333, 129.19333333333, 	65.6, 69.733333333333]
aws_no_lock_err = [0.51648383861991, 1.985032885258, 1.2078355296425, 0.73140655968863]

pyflink_means = [306.34666666667, 	5873, 348.32666666667, 602.79333333333]
pyflink_err = [3.7677962907897, 302.14051182999, 12.013143727694, 10.910451665974]

flink_means = [59.03, 	348.24666666667, 115.26333333333,	134.10333333333]
flink_err = [0.76056996171731, 31.634369846032, 5.3153885611078, 8.436864873215]
#

width = 0.23 # the width of the bars
x1 = np.arange(len(labels))  # the label locations
x2 = [x + width for x in x1]
x3 = [x + width for x in x2]
x4 = [x + width for x in x3]

fig, ax = plt.subplots()
rects2 = ax.bar(x1, aws_no_lock_means, width, label="AWS Lambda", yerr=aws_no_lock_err, capsize=4, color="#ef476f")
rects1 = ax.bar(
    x2, statefun_means, width, label="Statefun", yerr=statefun_err, capsize=4, color="#ffd166"
)
rects3 = ax.bar(x3, pyflink_means, width, label="PyFlink", yerr=pyflink_err, capsize=4, color="#118ab2")
rects4 = ax.bar(x4, flink_means, width, label="Flink JVM", yerr=flink_err, capsize=4, color="#06d6a0")

plt.legend()
ax.set_ylabel("Latency (in ms)")
ax.set_xticks([r + width for r in range(len(labels))])
ax.set_xticklabels(labels)
ax.annotate("5873 ms", xy=(x3[1], 760,), xytext=(x3[1], 850), color="black", ha="center", arrowprops=dict(arrowstyle='<-',lw=1.2))
#ax.arrow(x3[1], 780, 0.5, 1, head_width=1, head_length=0.1, fc='k', ec='k')
plt.ylim([0, 800])
plt.xlabel("HTTP endpoint")

ax.legend(loc='upper left')
fig.tight_layout()
plt.savefig("deathstar_endpoint.pdf")
plt.show()

# PLOT WITH BROKEN AXIS
# import matplotlib.pyplot as plt
# import numpy as np
#
# labels = ["login", "search", "reserve", "recommend"]
# statefun_means = [126.18333333333, 623.61333333333, 172.15666666667, 332.2]
# statefun_err = [0.16679994670929, 12.746755555556, 1.8244694814901, 2.050609665441]
#
# aws_means = [74.05, 293.46333333333, 73.643333333333, 130.28]
# aws_err = [0.15513435037627, 9.7107683641524, 1.5979222620502, 7.4055429690649]
#
#
# pyflink_means = [306.34666666667, 	5873, 348.32666666667, 602.79333333333]
# pyflink_err = [3.7677962907897, 302.14051182999, 12.013143727694, 10.910451665974]
#
# fig, (ax, ax2) = plt.subplots(2, 1, sharex=True)
#
# width = 0.28  # the width of the bars
# x1 = np.arange(len(labels))  # the label locations
# x2 = [x + width for x in x1]
# x3 = [x + width for x in x2]
#
# ax.set_ylim([5450, 6250])
# ax2.set_ylim([0, 800])
#
# rects1 = ax.bar(
#     x1, statefun_means, width, label="statefun", yerr=statefun_err, capsize=4
# )
# rects1 = ax2.bar(
#     x1, statefun_means, width, label="statefun", yerr=statefun_err, capsize=4
# )
# rects2 = ax.bar(x2, aws_means, width, label="aws", yerr=aws_err, capsize=4)
# rects2 = ax2.bar(x2, aws_means, width, label="aws", yerr=aws_err, capsize=4)
# rects3 = ax.bar(x3, pyflink_means, width, label="pyflink", yerr=pyflink_err, capsize=4)
# rects3 = ax2.bar(x3, pyflink_means, width, label="pyflink", yerr=pyflink_err, capsize=4)
#
# ax.spines['bottom'].set_visible(False)
# ax2.spines['top'].set_visible(False)
# ax.xaxis.tick_top()
# ax.tick_params(labeltop=False)  # don't put tick labels at the top
# ax2.xaxis.tick_bottom()
#
# d = .015  # how big to make the diagonal lines in axes coordinates
# # arguments to pass to plot, just so we don't keep repeating them
# kwargs = dict(transform=ax.transAxes, color='k', clip_on=False)
# ax.plot((-d, +d), (-d, +d), **kwargs)        # top-left diagonal
# ax.plot((1 - d, 1 + d), (-d, +d), **kwargs)  # top-right diagonal
#
# kwargs.update(transform=ax2.transAxes)  # switch to the bottom axes
# ax2.plot((-d, +d), (1 - d, 1 + d), **kwargs)  # bottom-left diagonal
# ax2.plot((1 - d, 1 + d), (1 - d, 1 + d), **kwargs)  # bottom-right diagonal
#
# ax.set_ylabel("Latency (in ms)")
# ax.set_xticks([r + width for r in range(len(labels))])
# ax.set_xticklabels(labels)
# #ax.text(x3[1], 900, "5873", color="black", ha="center", size="smaller", weight="heavy")
# plt.xlabel("Endpoint")
# ax.legend()
#
# fig.tight_layout()
# plt.show()
