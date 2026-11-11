"""Application 2 results: when does the W/Cu interface depart from equilibrium?

For each temperature and each bilayer scale (both thicknesses multiplied by the same
factor), run the transient with the interface as a manifold and as an algebraic
equilibrium condition, and record the time for the back-face flux to reach half its
steady value.

Writes ``transients.csv``, ``delay.csv`` and ``interface_trapping.pdf``.
Run with ``--plot`` to redraw from the CSVs without solving.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import pandas as pd
import parameters as P
from common import *
from model import run, steady_flux

HERE = pathlib.Path(__file__).resolve().parent
SCALES = np.logspace(-3, 0, 7)  # W thickness from 6 um to 6 mm
SHOWN = {340.0: [1.0, 1e-2]}  # transients kept for the figure


def timescales(T, scale):
    D_w = P.D_W_0 * np.exp(-P.E_D_W / (P.K_B * T))
    D_cu = P.D_CU_0 * np.exp(-P.E_D_CU / (P.K_B * T))
    r = P.rates(T)
    t_diff = (scale * P.L_W) ** 2 / D_w + (scale * P.L_CU) ** 2 / D_cu
    t_int = 1 / (r["i_to_w"] + r["i_to_cu"])
    return t_diff, t_int


def half_time(out, steady):
    return float(np.interp(0.5, out["flux"] / steady, out["t"]))


def main():
    rows, transients = [], []
    for T in P.TEMPERATURES:
        for scale in SCALES:
            t_diff, t_int = timescales(T, scale)
            final_time = 5 * t_diff + 30 * t_int
            steady = steady_flux(T, scale=scale)
            row = {"T": T, "scale": scale, "l_w": scale * P.L_W, "t_diff": t_diff,
                   "t_int": t_int, "steady_flux": steady}
            for kind in ("equilibrium", "manifold"):
                out = run(T, kind, final_time, scale=scale, first_step=min(t_diff, t_int) / 200)
                row[f"t_half_{kind}"] = half_time(out, steady)
                row[f"final_flux_{kind}"] = out["flux"][-1]
                if kind == "manifold":
                    row["coverage"] = out["interface"][-1] / P.N_SITES
                    row["interface_inventory"] = out["interface"][-1]
                    row["bulk_inventory"] = out["tungsten"][-1] + out["copper"][-1]
                if any(np.isclose(scale, s) for s in SHOWN.get(T, [])):
                    df = pd.DataFrame({"t": out["t"], "flux": out["flux"] / steady})
                    if kind == "manifold":
                        df["coverage"] = out["interface"] / P.N_SITES
                    transients.append(df.assign(T=T, scale=scale, kind=kind))
            rows.append(row)
            print({k: (f"{v:.3g}" if isinstance(v, float) else v) for k, v in row.items()}, flush=True)
    pd.DataFrame(rows).to_csv(HERE / "delay.csv", index=False)
    pd.concat(transients).to_csv(HERE / "transients.csv", index=False)
    plot()


def plot():
    delay = pd.read_csv(HERE / "delay.csv")
    transients = pd.read_csv(HERE / "transients.csv")

    fig, (ax, ax2) = plt.subplots(1, 2, figsize=(COL2, 2.5))
    for (scale, sub), colour in zip(
        sorted(transients.groupby("scale"), key=lambda g: -g[0]), (PALETTE[0], PALETTE[2])
    ):
        label = rf"$L_\mathrm{{W}}$ = {scale * P.L_W * 1e3:g} mm"
        man = sub[sub.kind == "manifold"]
        eq = sub[sub.kind == "equilibrium"]
        ax.semilogx(man.t, man.flux, color=colour, label=label)
        ax.semilogx(eq.t, eq.flux, color=colour, ls="--", lw=1.0)
    ax.plot([], [], color="grey", label="interface as a manifold")
    ax.plot([], [], color="grey", ls="--", lw=1.0, label="equilibrium condition")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Back-face flux / steady value")
    ax.set_ylim(0, 1.05)
    ax.legend(loc="upper left")
    ax.set_title(f"(a)  {list(SHOWN)[0]:.0f} K", loc="left")

    for (T, sub), colour in zip(delay.groupby("T"), PALETTE):
        ax2.loglog(sub.l_w * 1e3, sub.t_half_manifold / sub.t_half_equilibrium,
                   "o-", ms=3, color=colour, label=f"{T:.0f} K")
    ax2.axhline(1, color="grey", lw=0.6, ls=":")
    ax2.set_xlabel(r"Tungsten thickness $L_\mathrm{W}$ (mm)")
    ax2.set_ylabel("Breakthrough time relative\nto equilibrium condition")
    ax2.legend()
    ax2.set_title("(b)", loc="left")
    fig.tight_layout()
    savefig(fig, __file__, "interface_trapping")


if __name__ == "__main__":
    plot() if "--plot" in sys.argv else main()
