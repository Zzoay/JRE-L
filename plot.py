import matplotlib.pyplot as plt
import json


data = json.load(open('scores_elife.json', 'r'))

fig, ax = plt.subplots(figsize=(9, 6))

# ax.set_title("Metric Scores Over Round", fontsize=22)
ax.set_xlabel("Round", fontsize=24)
ax.set_ylabel("Score", fontsize=24)

ax.set_ylim(9, 15)

x_ticks = range(0, 7)
ax.set_xticks(x_ticks)
ax.set_yticks(range(10, 16))

# ax.set_yscale('log')
# ax.set_yticks(range(0, 70, 10))

markers = ['o', 's', 'p', '*', 'x', '>'] 

metric_dct = {
    "coleman-liau-index": "CLI", "flesch-kincaid-grade": "FKGL", "dale-chall-readability-score": "DCRS"
}

lines = []
# linestyles = ['--', ':', '-.', '-', '', '']
colors = ['goldenrod', 'maroon', 'forestgreen', 'navy', 'peru', 'olive']
for metric, values, m, c in zip(data.keys(), data.values(), markers, colors):
    if metric not in ["coleman-liau-index", "flesch-kincaid-grade", "dale-chall-readability-score"]:
        continue
    line, = ax.plot(values[1:7], label=metric_dct[metric], marker=m, color=c, linewidth=2, markersize=6)
    lines.append(line)

leg = ax.legend(loc='best', fontsize=18)

ax.tick_params(axis='x', labelsize=18) 
ax.tick_params(axis='y', labelsize=18) 

plt.show()

plt.savefig('elife.pdf')