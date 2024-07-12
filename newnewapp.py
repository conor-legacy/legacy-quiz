import matplotlib.pyplot as plt
import numpy as np

# Define the intervals and scores
ebitda_intervals = np.arange(0, 1000001, 200000)
scores = np.linspace(0, 100, len(ebitda_intervals))

# Define the multiples for each interval
multiples = np.linspace(1, 10, len(ebitda_intervals))

# Calculate the height of each bar segment
bar_segments = [score * multiple for score, multiple in zip(scores, multiples)]

# Plotting the bar chart
fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(ebitda_intervals, scores, color='green', label='Base Score')

for i in range(len(bars)):
    bottom = bars[i].get_height()
    height = bar_segments[i]
    ax.bar(ebitda_intervals[i], height, bottom=bottom, color='red', label='Multiple of EBITDA' if i == 0 else "")

ax.set_xlabel('EBITDA ($)')
ax.set_ylabel('Score')
ax.set_title('Business Valuation Quiz Score vs. EBITDA with Multiples')
ax.set_xticks(ebitda_intervals)
ax.set_ylim(0, 100)

# Ensure the legend is displayed correctly without duplicates
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys())

plt.show()
