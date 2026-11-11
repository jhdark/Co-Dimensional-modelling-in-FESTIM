"""Application 1 results: the permeator against its analytical solution.

Extraction efficiency ``1 - c_f(z) / c_in`` along the tube for the two published cases
(see ``cases.py``), and the start-up transient of the Pb-17Li case.

Writes ``efficiency.csv``, ``startup.csv`` and ``permeator.pdf``.
Run with ``--plot`` to redraw from the CSVs without solving.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
from cases import CASES, PBLI
from common import *
from model import build, steady

HERE = pathlib.Path(__file__).resolve().parent
STARTUP_TIME = 150.0  # s


def main():
    rows = []
    for case in CASES:
        z, cf = steady(case)
        eta = 1 - cf / case.c_in
        exact = case.efficiency(z)
        rows.append(pd.DataFrame({"case": case.name, "z": z, "festim": eta, "analytical": exact}))
        print(f"{case.name}: eta(L) FESTIM {eta[-1]:.4f}, analytical {exact[-1]:.4f}, "
              f"published {case.eta_published}, max abs. diff along the tube "
              f"{np.max(np.abs(eta - exact)):.2e}", flush=True)
    pd.concat(rows).to_csv(HERE / "efficiency.csv", index=False)

    model, *_ = build(PBLI, transient=True, final_time=STARTUP_TIME)
    model.initialise()
    model.run()
    export = model.exports[0]
    pd.DataFrame(
        {"t": export.t, "eta_outlet": 1 - np.array(export.data) / PBLI.c_in}
    ).to_csv(HERE / "startup.csv", index=False)
    plot()


def plot():
    df = pd.read_csv(HERE / "efficiency.csv")
    startup = pd.read_csv(HERE / "startup.csv")

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(COL2, 2.5))
    for case, colour in zip(CASES, (PALETTE[0], PALETTE[2])):
        sub = df[df.case == case.name]
        ax.plot(sub.z, sub.festim, color=colour, label=case.name)
        ax.plot(sub.z[::25], sub.analytical[::25], "o", ms=3, mfc="white", mec=colour,
                mew=0.8)
        ax.plot(case.length, case.eta_published[0], "*", ms=8, color=colour, mec="white",
                mew=0.5, zorder=5, clip_on=False)
    ax.plot([], [], "o", ms=3, mfc="white", mec="grey", mew=0.8, label="analytical")
    ax.plot([], [], "*", ms=8, color="grey", mec="white", mew=0.5, label="Rader et al.")
    ax.set_xlabel(r"Distance along the tube $z$ (m)")
    ax.set_ylabel("Extraction efficiency")
    ax.set_xlim(0, 50)
    ax.set_ylim(0, 0.8)
    ax.legend(loc="upper left")
    ax.set_title("(a)", loc="left")

    ax2.plot(startup.t, startup.eta_outlet, color=PALETTE[0], label="Pb-17Li / RAFM steel")
    ax2.axhline(float(PBLI.efficiency(PBLI.length)), color="grey", lw=0.8, ls="--",
                label="steady state, analytical")
    ax2.axvline(PBLI.length / PBLI.velocity, color="grey", lw=0.6, ls=":")
    ax2.text(PBLI.length / PBLI.velocity + 2, 0.05, "transit time", fontsize=7, color="grey")
    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Extraction efficiency at the outlet")
    ax2.set_xlim(0, STARTUP_TIME)
    ax2.set_ylim(0, 1.0)
    ax2.legend(loc="lower right")
    ax2.set_title("(b)", loc="left")
    fig.tight_layout()
    savefig(fig, __file__, "permeator")


if __name__ == "__main__":
    plot() if "--plot" in sys.argv else main()
