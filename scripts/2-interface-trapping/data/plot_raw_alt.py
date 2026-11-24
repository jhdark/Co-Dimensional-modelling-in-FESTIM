"""Plot the second delivery of raw MD data (new_data/, one file per interface and
temperature) to check the 1000 K series.

Figure 1: every file as points, the whole 20 ns. Points do not care about row order,
so this shows the data as they are.
Figure 2: the 1000 K files only, first 6 ns, rows joined by a line. On the left in
the order supplied (shuffled, so the line goes back and forth), on the right after
sorting by time and dropping the repeated rows.

Writes raw_alt_full.png and raw_alt_1000K.png next to this script.
"""

import pathlib

import matplotlib.pyplot as plt
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
INTERFACES = ["0001", "000-1"]
TEMPERATURES = [750, 1000, 1250]


def read(interface, T):
    """Rows as supplied: time (ns), N_D (m-2)."""
    name = HERE / "new_data" / f"D_trapped_at_{interface}_{T}K.csv"
    data = np.genfromtxt(name, delimiter=",", skip_header=1)
    return data[:, 0], data[:, 1]


def sort_and_dedupe(time, N):
    """Drop rows that appear twice, then put the rest in time order."""
    rows = np.unique(np.column_stack([time, N]), axis=0)  # also sorts by time
    return rows[:, 0], rows[:, 1]


# ---------------------------------------------------------------
# Figure 1: the whole 20 ns, all six files
# ---------------------------------------------------------------

fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)

for ax, interface in zip(axes, INTERFACES):
    for T in TEMPERATURES:
        time, N = read(interface, T)
        ax.plot(time, N, ".", markersize=2, label=f"{T} K ({len(time)} rows)")
    ax.set_title(f"D_trapped_at_{interface}_*K.csv")
    ax.set_xlabel("time (ns)")
    ax.legend(markerscale=4)
axes[0].set_ylabel("N_D (m-2)")

fig.tight_layout()
fig.savefig(HERE / "raw_alt_full.png", dpi=150)


# ---------------------------------------------------------------
# Figure 2: 1000 K, first 6 ns, as supplied against sorted
# ---------------------------------------------------------------

fig, axes = plt.subplots(2, 2, figsize=(11, 7), sharex=True, sharey="row")

for row, interface in zip(axes, INTERFACES):
    time, N = read(interface, 1000)
    time_sorted, N_sorted = sort_and_dedupe(time, N)
    print(
        f"{interface} 1000 K: {len(time)} rows supplied, "
        f"{np.sum(np.diff(time) < 0)} steps backwards in time, "
        f"{len(time_sorted)} rows after dropping repeats"
    )

    start = time <= 6
    row[0].plot(time[start], N[start], ".-", linewidth=0.3, markersize=2, color="C1")
    row[0].set_title(f"{interface}, 1000 K, as supplied")
    row[0].set_ylabel("N_D (m-2)")

    start = time_sorted <= 6
    row[1].plot(time_sorted[start], N_sorted[start], ".-", linewidth=0.3, markersize=2, color="C1")
    row[1].set_title(f"{interface}, 1000 K, sorted by time, repeats dropped")

for ax in axes[1]:
    ax.set_xlabel("time (ns)")

fig.tight_layout()
fig.savefig(HERE / "raw_alt_1000K.png", dpi=150)

plt.show()
