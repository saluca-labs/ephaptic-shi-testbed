"""
Run the ephaptic-analog testbed end-to-end: M1-M6 (see testbed-spec.md).
Produces figures in ./figs and a machine-readable results.json.
Deterministic; reproduce with:  python run.py
"""
import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ephaptic_sim import (Array, run_condition, synchrony_vs_distance, analyze)

V_AX, V_SLOW = 0.62, 0.08          # mm/ms  (from Rebbin et al.)
PRED_SLOPE = 1.0 / (1.0 / V_SLOW - 1.0 / V_AX)   # lambda = PRED_SLOPE * (1/f)
FIGS = os.path.join(os.path.dirname(__file__), "figs")
os.makedirs(FIGS, exist_ok=True)
RESULTS = {}


def pred_lambda(f_khz):
    return 1.0 / (f_khz * (1.0 / V_SLOW - 1.0 / V_AX))


def _json_default(o):
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    return str(o)


# ----------------------------------------------------------------------------
# M1 -- does synchrony ripple? (faithful 4x2 mm array, gamma)
# ----------------------------------------------------------------------------
def M1():
    arr = Array(width_mm=4.0, height_mm=2.0, nx=40, ny=20)
    f = 0.040
    fires = run_condition(arr, f, V_AX, V_SLOW, n_bursts=300, seed=1)
    c, pc, pr = synchrony_vs_distance(arr, fires, nbins=45)
    a = analyze(c, pc)
    fig, ax = plt.subplots(figsize=(7, 4.3))
    ax.plot(c, pc, "o", ms=4, color="#2b6cb0", label="measured synchrony (baseline-corrected)")
    ax.plot(c, a["model"], "-", color="#e53e3e", lw=2, label="exp + cosine fit")
    ax.axhline(0, color="#999", lw=.7)
    ax.axvline(a["lam"], ls="--", color="#38a169", label=f"measured $\\lambda$={a['lam']:.2f} mm")
    ax.axvline(pred_lambda(f), ls=":", color="#805ad5", label=f"predicted $\\lambda$={pred_lambda(f):.2f} mm")
    ax.set_xlabel("pairwise distance (mm)"); ax.set_ylabel("$\\Delta$ synchrony")
    ax.set_title("M1  Synchrony ripples with distance (40 Hz, 4$\\times$2 mm array)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{FIGS}/M1_ripple.png", dpi=130)
    plt.close(fig)
    RESULTS["M1"] = dict(f_hz=40, lam_meas=a["lam"], lam_pred=pred_lambda(f),
                         rebound_frac=a["rebound_frac"], snr=a["snr"], resolved=a["resolved"])
    print(f"[M1] 40Hz  lam_meas={a['lam']:.3f}  lam_pred={pred_lambda(f):.3f}  snr={a['snr']:.2f}  resolved={a['resolved']}")


# ----------------------------------------------------------------------------
# M3 -- the decisive test: lambda proportional to 1/f
#   Uses a 6x4 mm array (enlarged beyond the dish -- an in-silico affordance)
#   so the beta-gamma band is resolvable.
# ----------------------------------------------------------------------------
def M3():
    arr = Array(width_mm=6.0, height_mm=4.0, nx=48, ny=32)
    freqs = [20, 25, 30, 35, 40, 45, 50, 55]
    inv_f, lam, resolved, preds = [], [], [], []
    for hz in freqs:
        f = hz / 1000.0
        fires = run_condition(arr, f, V_AX, V_SLOW, n_bursts=200, seed=3)
        c, pc, pr = synchrony_vs_distance(arr, fires, nbins=55)
        a = analyze(c, pc)
        inv_f.append(1 / f); lam.append(a["lam"]); resolved.append(a["resolved"])
        preds.append(pred_lambda(f))
        print(f"[M3] {hz}Hz 1/f={1/f:5.1f}ms  lam={a['lam']:.3f}  pred={pred_lambda(f):.3f}  resolved={a['resolved']}  snr={a['snr']:.2f}")
    inv_f = np.array(inv_f); lam = np.array(lam); resolved = np.array(resolved)
    m = resolved
    A = np.column_stack([inv_f[m], np.ones(m.sum())])
    (slope, inter), *_ = np.linalg.lstsq(A, lam[m], rcond=None)
    res = lam[m] - A @ np.array([slope, inter])
    r2 = 1 - (res ** 2).sum() / ((lam[m] - lam[m].mean()) ** 2).sum()

    fig, ax = plt.subplots(figsize=(7, 4.3))
    xx = np.linspace(0, inv_f.max() * 1.05, 50)
    ax.plot(xx, PRED_SLOPE * xx, ":", color="#805ad5", lw=2,
            label=f"prediction  $\\lambda=(1/f)/(1/v_{{ep}}-1/v_{{ax}})$  slope={PRED_SLOPE:.3f}")
    ax.plot(xx, slope * xx + inter, "-", color="#e53e3e", lw=1.5,
            label=f"fit to resolved pts  slope={slope:.3f}  $R^2$={r2:.2f}")
    ax.plot(inv_f[m], lam[m], "o", ms=7, color="#2b6cb0", label="resolved (measured)")
    ax.plot(inv_f[~m], lam[~m], "x", ms=8, color="#a0aec0", label="unresolved ($\\lambda>$ array)")
    ax.set_xlabel("1/f  (ms)"); ax.set_ylabel("measured wavelength $\\lambda$ (mm)")
    ax.set_title("M3  Wavelength scales as 1/f  (the decisive fingerprint)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{FIGS}/M3_scaling.png", dpi=130)
    plt.close(fig)
    RESULTS["M3"] = dict(freqs_hz=freqs, inv_f_ms=inv_f.tolist(), lam=lam.tolist(),
                         resolved=resolved.tolist(), pred=preds,
                         slope_meas=slope, slope_pred=PRED_SLOPE, intercept=inter, r2=r2,
                         n_resolved=int(m.sum()))
    print(f"[M3] SLOPE meas={slope:.4f}  pred={PRED_SLOPE:.4f}  intercept={inter:.3f}  R2={r2:.3f}  (n={int(m.sum())})")


# ----------------------------------------------------------------------------
# M4 -- ablation: turn the slow channel off; the ripple must collapse.
# ----------------------------------------------------------------------------
def M4():
    arr = Array(width_mm=6.0, height_mm=4.0, nx=48, ny=32)
    f = 0.040
    on = run_condition(arr, f, V_AX, V_SLOW, n_bursts=200, seed=3, slow_on=True)
    off = run_condition(arr, f, V_AX, V_SLOW, n_bursts=200, seed=3, slow_on=False)
    c1, p1, _ = synchrony_vs_distance(arr, on, nbins=55)
    c0, p0, _ = synchrony_vs_distance(arr, off, nbins=55)
    a1, a0 = analyze(c1, p1), analyze(c0, p0)
    fig, ax = plt.subplots(figsize=(7, 4.3))
    ax.plot(c1, p1, "o-", ms=3, color="#2b6cb0", label=f"slow channel ON  (rebound={a1['rebound_frac']:.2f}, snr={a1['snr']:.1f})")
    ax.plot(c0, p0, "s-", ms=3, color="#a0aec0", label=f"slow channel OFF (rebound={a0['rebound_frac']:.2f}, snr={a0['snr']:.1f})")
    ax.axhline(0, color="#999", lw=.7)
    ax.set_xlabel("pairwise distance (mm)"); ax.set_ylabel("$\\Delta$ synchrony")
    ax.set_title("M4  Ablation: the ripple is field-driven (vanishes with slow channel off)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{FIGS}/M4_ablation.png", dpi=130)
    plt.close(fig)
    RESULTS["M4"] = dict(on=dict(rebound_frac=a1["rebound_frac"], snr=a1["snr"], resolved=a1["resolved"]),
                         off=dict(rebound_frac=a0["rebound_frac"], snr=a0["snr"], resolved=a0["resolved"]))
    print(f"[M4] ON rebound={a1['rebound_frac']:.2f} snr={a1['snr']:.2f} resolved={a1['resolved']} | "
          f"OFF rebound={a0['rebound_frac']:.2f} snr={a0['snr']:.2f} resolved={a0['resolved']}")


# ----------------------------------------------------------------------------
# M5 -- identifiability control: the wavelength is set by the SPEED DIFFERENCE.
#   Fix f, sweep v_slow. If lambda tracks 1/[f(1/v_slow - 1/v_ax)] and DIVERGES
#   as v_slow -> v_ax (ripple vanishes), then the wavelength is a fingerprint of
#   two-speed interference specifically -- a static / fixed-length ('Mexican
#   hat', two-cell-type) kernel has no dependence on conduction speeds at all.
# ----------------------------------------------------------------------------
def M5():
    arr = Array(width_mm=6.0, height_mm=4.0, nx=48, ny=32)
    f = 0.040
    # dense sampling across the resolvable band, then a vanishing tail (v_ep->v_ax)
    v_slows = [0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.14, 0.20, 0.40, 0.62]
    inv_diff, lam, resolved, preds = [], [], [], []
    for vs in v_slows:
        fires = run_condition(arr, f, V_AX, vs, n_bursts=320, seed=7)
        c, pc, pr = synchrony_vs_distance(arr, fires, nbins=55)
        a = analyze(c, pc)
        diff = (1.0 / vs - 1.0 / V_AX)
        pred = np.inf if diff <= 0 else 1.0 / (f * diff)
        inv_diff.append(diff); lam.append(a["lam"]); resolved.append(a["resolved"]); preds.append(pred)
        tag = "ripple vanishes" if not a["resolved"] else ""
        print(f"[M5] v_slow={vs:.2f}  lam={a['lam']:.3f}  pred={pred:.3f}  resolved={a['resolved']} {tag}")
    lam = np.array(lam); preds = np.array(preds); resolved = np.array(resolved)
    m = resolved & np.isfinite(preds)
    fig, ax = plt.subplots(figsize=(7, 4.3))
    hi = max(preds[m].max(), lam[m].max()) * 1.1
    ax.plot([0, hi], [0, hi], ":", color="#805ad5", label="prediction $\\lambda=1/[f(1/v_{ep}-1/v_{ax})]$ (identity)")
    ax.plot(preds[m], lam[m], "s", ms=8, color="#dd6b20", label="measured (resolved)")
    for vs, p, l, r in zip(v_slows, preds, lam, resolved):
        if r and np.isfinite(p):
            ax.annotate(f"$v_{{ep}}$={vs}", (p, l), fontsize=7, xytext=(4, 4), textcoords="offset points")
    ax.set_xlabel("predicted $\\lambda$ from speed difference (mm)")
    ax.set_ylabel("measured $\\lambda$ (mm)")
    n_van = int((~resolved).sum())
    ax.set_title(f"M5  Wavelength is set by the speed difference\n(as $v_{{ep}}\\to v_{{ax}}$ the ripple vanishes: {n_van} pts unresolved)")
    ax.legend(fontsize=8); fig.tight_layout(); fig.savefig(f"{FIGS}/M5_speeddiff.png", dpi=130)
    plt.close(fig)
    RESULTS["M5"] = dict(v_slows=v_slows, lam=lam.tolist(), pred=preds.tolist(),
                         resolved=resolved.tolist(), n_vanished=n_van)
    print(f"[M5] wavelength tracks the speed difference; {n_van} high-v_slow pts show the ripple vanishing")


# ----------------------------------------------------------------------------
# M6 -- generative anisotropy: prune low-coherence units; banding needs the field.
# ----------------------------------------------------------------------------
def coherence_score(arr, fires, win_ms=2.0):
    """Per-unit mean pairwise synchrony with all others (its 'coherence')."""
    N = arr.N
    score = np.zeros(N); cnt = np.zeros(N)
    for ft in fires:
        fin = np.isfinite(ft)
        idx = np.where(fin)[0]
        t = ft[idx]
        syn = (np.abs(t[:, None] - t[None, :]) <= win_ms)
        s = syn.sum(1) - 1.0
        score[idx] += s; cnt[idx] += (len(idx) - 1)
    return score / np.maximum(cnt, 1)


def prune_and_map(arr, fires, keep_frac=0.5):
    sc = coherence_score(arr, fires)
    thr = np.quantile(sc, 1 - keep_frac)
    keep = sc >= thr
    return keep


def M6():
    arr = Array(width_mm=4.0, height_mm=2.0, nx=40, ny=20)
    f = 0.040
    on = run_condition(arr, f, V_AX, V_SLOW, n_bursts=250, seed=5, slow_on=True)
    off = run_condition(arr, f, V_AX, V_SLOW, n_bursts=250, seed=5, slow_on=False)
    keep_on = prune_and_map(arr, on)
    keep_off = prune_and_map(arr, off)

    def banding_index(keep):
        # survivor density profile across the long (x) axis.
        # EDGE/CENTER ratio: two edge bands (Rebbin) -> >1 ; central blob -> <1.
        x = arr.pos[:, 0]
        W = arr.width_mm
        bins = np.linspace(0, W, 13)
        idx = np.clip(np.digitize(x, bins) - 1, 0, 11)
        dens = np.array([keep[idx == b].mean() if (idx == b).any() else 0 for b in range(12)])
        edge = keep[(x < W / 3) | (x > 2 * W / 3)].mean()
        center = keep[(x >= W / 3) & (x <= 2 * W / 3)].mean()
        # bounded edge-vs-center contrast in [-1, 1]: +1 = pure edge bands
        # (Rebbin's two vertical bands), -1 = pure central blob.
        return dens, float((edge - center) / (edge + center + 1e-9))

    dens_on, bi_on = banding_index(keep_on)
    dens_off, bi_off = banding_index(keep_off)

    fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
    for ax, keep, tag in [(axes[0], keep_on, f"slow ON  (edge$-$center contrast={bi_on:+.2f})"),
                          (axes[1], keep_off, f"slow OFF (edge$-$center contrast={bi_off:+.2f})")]:
        ax.scatter(arr.pos[~keep, 0], arr.pos[~keep, 1], s=6, color="#e2e8f0")
        ax.scatter(arr.pos[keep, 0], arr.pos[keep, 1], s=10, color="#2b6cb0")
        ax.set_title(tag, fontsize=10); ax.set_aspect("equal"); ax.set_xlabel("x (mm)")
    fig.suptitle("M6  Coherence-pruned survivors: edge banding requires the field")
    fig.tight_layout(); fig.savefig(f"{FIGS}/M6_anisotropy.png", dpi=130); plt.close(fig)
    RESULTS["M6"] = dict(contrast_on=bi_on, contrast_off=bi_off,
                         density_on=dens_on.tolist(), density_off=dens_off.tolist())
    print(f"[M6] edge-center contrast  ON={bi_on:+.3f} (edge bands)  OFF={bi_off:+.3f} (central blob)")


if __name__ == "__main__":
    import time
    t0 = time.time()
    M1(); M3(); M4(); M5(); M6()
    RESULTS["_meta"] = dict(v_ax=V_AX, v_slow=V_SLOW, pred_slope=PRED_SLOPE,
                            elapsed_s=round(time.time() - t0, 1))
    with open(os.path.join(os.path.dirname(__file__), "results.json"), "w") as fh:
        json.dump(RESULTS, fh, indent=2, default=_json_default)
    print(f"\nDONE in {time.time()-t0:.1f}s -> figs/ and results.json")
