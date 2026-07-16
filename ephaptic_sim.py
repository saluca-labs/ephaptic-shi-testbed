"""
Ephaptic-analog testbed: two-channel interference in a neuron-free medium.

Design contract (see testbed-spec.md):
  * The two channel SPEEDS are inputs (they ARE the hypothesis being tested).
  * The synchrony-vs-distance curve and its wavelength are MEASURED OUTPUTS.
    No line of code computes lambda = 1/[f(1/v_ep - 1/v_ax)]; that relation,
    if it appears, emerges from the measured spike trains.

Local rule per agent i, per burst originating at source s:
  - FAST channel (analog of directed broker messages / axonal spikes):
      an excitatory 'arm' pulse reaches i at delay  d(i,s)/v_ax.
  - SLOW channel (analog of shared-memory field / ephaptic phase):
      i's local oscillator phase is offset by the slow wave, t0_i = d(i,s)/v_slow.
  - FIRING: once armed, i integrates and fires at the NEXT tick its local
      field enters the receptive window (near peak). This 'integrate to next
      receptive phase' is stepped in real ticks, not solved in closed form.

Everything is deterministic given `seed` (numpy RandomState only; no wall clock).
"""

import numpy as np


class Array:
    """A rectangular lattice of agents, mirroring the 4x2 mm HDMEA aspect ratio."""

    def __init__(self, width_mm=4.0, height_mm=2.0, nx=40, ny=20):
        xs = np.linspace(0, width_mm, nx)
        ys = np.linspace(0, height_mm, ny)
        gx, gy = np.meshgrid(xs, ys)
        self.pos = np.column_stack([gx.ravel(), gy.ravel()])  # (N,2), mm
        self.N = self.pos.shape[0]
        self.width_mm = width_mm
        self.height_mm = height_mm
        # pairwise distances, precomputed once (used only by the MEASUREMENT stage)
        diff = self.pos[:, None, :] - self.pos[None, :, :]
        self.dist = np.sqrt((diff ** 2).sum(-1))  # (N,N) mm


def simulate_burst(arr, source_xy, f_khz, v_ax, v_slow, dt=0.2, T_ms=160.0,
                   recept=0.7, jitter_ms=0.6, rng=None, slow_on=True):
    """Run one burst; return fire time (ms) per agent, NaN if it never fired.

    f_khz: oscillation frequency in cycles/ms (e.g. 0.040 == 40 Hz).
    recept: field threshold for the receptive window, field = cos(2*pi*phase).
    """
    if rng is None:
        rng = np.random.RandomState(0)
    N = arr.N
    d = np.sqrt(((arr.pos - np.asarray(source_xy)) ** 2).sum(-1))  # (N,)
    tau_fast = d / v_ax          # fast 'arm' arrival time  (the ONLY fast input)
    t0 = d / v_slow if slow_on else np.zeros(N)  # slow phase offset (slow input)

    nsteps = int(T_ms / dt)
    fired = np.zeros(N, dtype=bool)
    fire_t = np.full(N, np.nan)

    for k in range(nsteps):
        t = k * dt
        armed = (t >= tau_fast) & (~fired)
        if not armed.any():
            if t > tau_fast.max():
                break
            continue
        if slow_on:
            field = np.cos(2 * np.pi * f_khz * (t - t0))
            receptive = field > recept
        else:
            # No slow channel -> no phase gate: fire as soon as armed.
            receptive = np.ones(N, dtype=bool)
        fire_now = armed & receptive
        if fire_now.any():
            fire_t[fire_now] = t
            fired[fire_now] = True

    # sub-threshold timing jitter (does not change WHETHER a unit fired)
    j = rng.normal(0, jitter_ms, N)
    fire_t = fire_t + j
    return fire_t


def simulate_burst_static(arr, source_xy, v_ax, wavelength_mm=1.5, amp_ms=1.8,
                          rng=None, **_ignore):
    """M5 control: a STATIC alternative generator with a FIXED spatial length
    scale and NO frequency dependence -- a stand-in for the short-range-excite /
    long-range-inhibit ('Mexican hat', two-cell-type) family. It deliberately
    imposes a synchrony ripple, but at a hard-coded wavelength. If it reproduces
    Rebbin's ripple yet CANNOT reproduce lambda proportional to 1/f, then the
    frequency-scaling is the fingerprint that distinguishes the dynamic two-speed
    mechanism from any static one. That is the identifiability test.
    """
    if rng is None:
        rng = np.random.RandomState(0)
    d = np.sqrt(((arr.pos - np.asarray(source_xy)) ** 2).sum(-1))
    tau_fast = d / v_ax
    # fixed-wavelength latency modulation -> fixed-lambda synchrony ripple, freq-free
    fire_t = tau_fast + amp_ms * np.cos(2 * np.pi * d / wavelength_mm)
    fire_t = fire_t + rng.normal(0, 0.6, arr.N)
    return fire_t


def synchrony_vs_distance(arr, fire_times, win_ms=2.0, nbins=45, dmax=None):
    """Baseline-corrected conditional firing probability vs pairwise distance.

    fire_times: list of (N,) arrays, one per burst.
    Returns (bin_centers, P_sync_corrected).
    """
    N = arr.N
    if dmax is None:
        dmax = arr.dist.max()
    edges = np.linspace(0, dmax, nbins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])

    iu = np.triu_indices(N, k=1)          # unique unordered pairs
    dpair = arr.dist[iu]                   # (P,)
    binidx = np.clip(np.digitize(dpair, edges) - 1, 0, nbins - 1)
    valid_mask = (dpair <= dmax)

    sync_count = np.zeros(nbins)
    total_count = np.zeros(nbins)
    for ft in fire_times:
        ti = ft[iu[0]]
        tj = ft[iu[1]]
        both = np.isfinite(ti) & np.isfinite(tj) & valid_mask
        syn = both & (np.abs(ti - tj) <= win_ms)
        total_count += np.bincount(binidx[both], minlength=nbins)
        sync_count += np.bincount(binidx[syn], minlength=nbins)

    with np.errstate(invalid='ignore', divide='ignore'):
        p = sync_count / total_count
    # baseline = grand mean synchrony rate across all pairs
    baseline = sync_count.sum() / total_count.sum()
    return centers, p - baseline, p


def fit_wavelength(centers, p_corr, lam_grid=None, xi_grid=None):
    """Fit  A*exp(-d/xi) + B*cos(2*pi*d/lam + phi)  by grid-searching (xi, lam)
    over an UNBIASED grid (no seeding from the theoretical value) and solving the
    linear amplitudes/phase by least squares. Returns best (lam, xi, r2, model).
    """
    good = np.isfinite(p_corr)
    d = centers[good]
    y = p_corr[good]
    if lam_grid is None:
        lam_grid = np.linspace(0.4, 6.0, 280)      # mm, wide & agnostic
    if xi_grid is None:
        xi_grid = np.linspace(0.3, 8.0, 60)

    best = (np.nan, np.nan, -np.inf, None)
    for xi in xi_grid:
        e = np.exp(-d / xi)
        for lam in lam_grid:
            c = np.cos(2 * np.pi * d / lam)
            s = np.sin(2 * np.pi * d / lam)
            X = np.column_stack([e, c, s, np.ones_like(d)])
            coef, *_ = np.linalg.lstsq(X, y, rcond=None)
            model = X @ coef
            ss_res = ((y - model) ** 2).sum()
            ss_tot = ((y - y.mean()) ** 2).sum()
            r2 = 1 - ss_res / ss_tot if ss_tot > 0 else -np.inf
            # require the oscillatory part to carry real amplitude
            osc_amp = np.hypot(coef[1], coef[2])
            exp_amp = abs(coef[0])
            if r2 > best[2] and osc_amp > 0.15 * (exp_amp + 1e-9):
                full = np.exp(-centers / xi) * coef[0] + \
                    coef[1] * np.cos(2 * np.pi * centers / lam) + \
                    coef[2] * np.sin(2 * np.pi * centers / lam) + coef[3]
                best = (lam, xi, r2, full)
    return best


def _fit_exp(d, y):
    """Pure monotonic fit A*exp(-d/xi)+C over an xi grid; return (r2, model_full, centers_kept)."""
    best = (-np.inf, None, np.nan)
    for xi in np.linspace(0.3, 12.0, 80):
        X = np.column_stack([np.exp(-d / xi), np.ones_like(d)])
        coef, *_ = np.linalg.lstsq(X, y, rcond=None)
        m = X @ coef
        ss_res = ((y - m) ** 2).sum()
        ss_tot = ((y - y.mean()) ** 2).sum()
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else -np.inf
        if r2 > best[0]:
            best = (r2, coef, xi)
    return best


def analyze(centers, p_corr, lam_grid=None):
    """Distinguish a genuine ripple from monotonic decay, and MEASURE its
    wavelength from the exponential-detrended residual (unbiased periodogram).

    Returns dict with:
      lam        : wavelength (mm) at the residual periodogram peak; MEASURED
      xi         : exponential decay length
      resolved   : True iff lam is meaningfully inside the array (can be trusted)
      r2_exp     : fit of pure monotonic exponential
      r2_osc     : fit of exponential + the detected sinusoid
      delta_r2   : oscillatory variance explained (ripple strength)
      rebound_frac : non-monotonic rise after the dip / total range (0 = monotonic)
      power_ratio: periodogram peak power / mean power (peak sharpness)
    """
    good = np.isfinite(p_corr)
    d = centers[good]
    y = p_corr[good]
    dmax = d.max()

    r2_exp, exp_coef, exp_xi = _fit_exp(d, y)
    # joint exp + cosine grid search (wavelength capped at the array size)
    if lam_grid is None:
        lam_grid = np.linspace(0.5, 0.95 * dmax, 320)
    lam_grid = lam_grid[lam_grid <= 0.98 * dmax]
    lam, xi, r2_osc, full = fit_wavelength(centers, p_corr, lam_grid=lam_grid)
    if full is None or not np.ndim(full):        # fit found no valid oscillation
        lam = float(lam_grid.max()); xi = exp_xi; r2_osc = r2_exp
        full = exp_coef[0] * np.exp(-centers / exp_xi) + exp_coef[1]

    # smoothed non-monotonic rebound (robust to per-bin noise): how far the
    # curve climbs back after its minimum. ~0 for a monotonic decay. Exclude
    # the last 3 bins from the minimum search so an edge plateau isn't the 'dip'.
    from scipy.ndimage import uniform_filter1d
    ys = uniform_filter1d(y, size=3, mode="nearest")
    imin = int(np.argmin(ys[:max(len(ys) - 3, 1)]))
    rebound = float(ys[imin:].max() - ys[imin])
    rng = float(y.max() - y.min()) + 1e-9
    rebound_frac = rebound / rng

    # oscillatory amplitude vs local scatter (diagnostic only)
    fm = np.interp(d, centers, full)
    resid_std = np.std(y - fm) + 1e-9
    c = np.cos(2 * np.pi * d / lam); s = np.sin(2 * np.pi * d / lam)
    X = np.column_stack([np.exp(-d / xi), c, s, np.ones_like(d)])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    osc_amp = float(np.hypot(coef[1], coef[2]))
    snr = osc_amp / resid_std

    # 'resolved': wavelength is trustworthy -- inside the array, off the grid
    # edge, above the bin size -- AND there is a genuine non-monotonic rebound
    # (the ripple hallmark; a monotonic decay has none).
    bin_w = centers[1] - centers[0]
    lam_edge = lam >= 0.95 * lam_grid.max()
    resolved = ((2 * bin_w < lam < dmax / 1.4) and (not lam_edge)
                and (rebound_frac > 0.08))
    return dict(lam=lam, xi=xi, resolved=resolved, r2_exp=r2_exp, r2_osc=r2_osc,
                delta_r2=r2_osc - r2_exp, rebound=rebound, rebound_frac=rebound_frac,
                osc_amp=osc_amp, snr=snr, model=full)


def run_condition(arr, f_khz, v_ax, v_slow, n_bursts=200, seed=1,
                  slow_on=True, static=False, **kw):
    """Generate spikes over many bursts (sources sampled across the array)."""
    rng = np.random.RandomState(seed)
    # sources sampled across the whole array (not just an edge) for generality
    srcs = np.column_stack([
        rng.uniform(0, arr.width_mm, n_bursts),
        rng.uniform(0, arr.height_mm, n_bursts),
    ])
    fires = []
    for b in range(n_bursts):
        brng = np.random.RandomState(seed * 100003 + b)
        if static:
            ft = simulate_burst_static(arr, srcs[b], v_ax, rng=brng, **kw)
        else:
            ft = simulate_burst(arr, srcs[b], f_khz, v_ax, v_slow,
                                rng=brng, slow_on=slow_on, **kw)
        fires.append(ft)
    return fires
