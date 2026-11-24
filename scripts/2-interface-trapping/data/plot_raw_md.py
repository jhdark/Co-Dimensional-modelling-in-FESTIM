import matplotlib.pyplot as plt
import numpy as np

# read the two files
# columns: time(ns), N_D_at_750K, N_D_at_1000K, N_D_at_1250K
data_0001 = np.genfromtxt("D_trapped_at_0001.csv", delimiter=",", skip_header=1)
data_000m1 = np.genfromtxt("D_trapped_at_000-1.csv", delimiter=",", skip_header=1)

time_0001 = data_0001[:, 0]
N_750K_0001 = data_0001[:, 1]
N_1000K_0001 = data_0001[:, 2]
N_1250K_0001 = data_0001[:, 3]

time_000m1 = data_000m1[:, 0]
N_750K_000m1 = data_000m1[:, 1]
N_1000K_000m1 = data_000m1[:, 2]
N_1250K_000m1 = data_000m1[:, 3]


# ---------------------------------------------------------------
# Figure 1: the whole 20 ns
# ---------------------------------------------------------------

fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4))

left.plot(time_0001, N_750K_0001, ".", markersize=2, label="750 K")
left.plot(time_0001, N_1000K_0001, ".", markersize=2, label="1000 K")
left.plot(time_0001, N_1250K_0001, ".", markersize=2, label="1250 K")
left.set_title("D_trapped_at_0001.csv")
left.set_xlabel("time (ns)")
left.set_ylabel("N_D (m-2)")
left.legend(markerscale=4)

right.plot(time_000m1, N_750K_000m1, ".", markersize=2, label="750 K")
right.plot(time_000m1, N_1000K_000m1, ".", markersize=2, label="1000 K")
right.plot(time_000m1, N_1250K_000m1, ".", markersize=2, label="1250 K")
right.set_title("D_trapped_at_000-1.csv")
right.set_xlabel("time (ns)")
right.set_ylabel("N_D (m-2)")
right.legend(markerscale=4)

fig.tight_layout()


# ---------------------------------------------------------------
# Figure 2: the first 0.5 ns, consecutive rows joined by a line
# ---------------------------------------------------------------

start_0001 = time_0001 <= 0.5
start_000m1 = time_000m1 <= 0.5

fig, (left, right) = plt.subplots(1, 2, figsize=(11, 4))

left.plot(time_0001[start_0001], N_750K_0001[start_0001], ".-", linewidth=0.5, label="750 K")
left.plot(time_0001[start_0001], N_1000K_0001[start_0001], ".-", linewidth=0.5, label="1000 K")
left.plot(time_0001[start_0001], N_1250K_0001[start_0001], ".-", linewidth=0.5, label="1250 K")
left.set_title("D_trapped_at_0001.csv, first 0.5 ns")
left.set_xlabel("time (ns)")
left.set_ylabel("N_D (m-2)")
left.legend()

right.plot(time_000m1[start_000m1], N_750K_000m1[start_000m1], ".-", linewidth=0.5, label="750 K")
right.plot(time_000m1[start_000m1], N_1000K_000m1[start_000m1], ".-", linewidth=0.5, label="1000 K")
right.plot(time_000m1[start_000m1], N_1250K_000m1[start_000m1], ".-", linewidth=0.5, label="1250 K")
right.set_title("D_trapped_at_000-1.csv, first 0.5 ns")
right.set_xlabel("time (ns)")
right.set_ylabel("N_D (m-2)")
right.legend()

fig.tight_layout()

plt.show()
