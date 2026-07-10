"""Generate the manuscript figures (doc/paper/paper_draft.md) into doc/figures/.

Five figures, every data panel regenerated from the same frozen rigs and
cached runs the paper's tables cite — no hand-drawn data:

  fig1  pipeline schematic (no data)
  fig2  ghost state: regimes + support boundary vs single-model T2
        (rig: tests/probes/test_regime_ghost_state.py)
  fig3  worked consumer: margin trajectory grades what BIP saturates
        (rig: tests/probes/test_downstream_policy.py)
  fig4  frozen-config transfer: realized FAR vs designed, detection
        paired (numbers: tests/multivariate/exp_frozen_transfer.py run, table A10)
  fig5  Mode A/B bimodality: per-file sweep separability distribution
        (cache: nab_score_cache/lambda3_tier2_cal.npz)

Colors are the validated reference categorical palette (dataviz skill);
subsets re-validated for adjacency (CVD >= 12 or direct labels present).

Usage::
    python -m tests.figures.make_figures            # all
    python -m tests.figures.make_figures fig3 fig4  # subset
"""

from __future__ import annotations

import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch

OUT = os.path.join(os.path.dirname(__file__), '..', '..', 'doc', 'figures')

BLUE, AQUA, YELLOW = '#2a78d6', '#1baf7a', '#eda100'
VIOLET, RED, ORANGE = '#4a3aa7', '#e34948', '#eb6834'
INK, INK2, GRID = '#0b0b0b', '#52514e', '#d9d8d4'

plt.rcParams.update({
    'font.size': 8, 'axes.titlesize': 8.5, 'axes.labelsize': 8,
    'axes.linewidth': 0.6, 'axes.edgecolor': INK2,
    'axes.labelcolor': INK, 'text.color': INK,
    'xtick.color': INK2, 'ytick.color': INK2,
    'xtick.labelsize': 7.5, 'ytick.labelsize': 7.5,
    'legend.fontsize': 7.5, 'legend.frameon': False,
    'grid.color': GRID, 'grid.linewidth': 0.5,
    'savefig.bbox': 'tight', 'savefig.dpi': 300,
})


def _save(fig, name):
    os.makedirs(OUT, exist_ok=True)
    for ext in ('pdf', 'png'):
        fig.savefig(os.path.join(OUT, f'{name}.{ext}'))
    plt.close(fig)
    print(f'  wrote doc/figures/{name}.pdf/.png')


# ------------------------------------------------------------------ fig1
def fig1():
    """Pipeline schematic: stream -> normal structure -> payload -> policy."""
    fig, ax = plt.subplots(figsize=(7.0, 2.4))
    ax.set_xlim(0, 100); ax.set_ylim(0, 30); ax.axis('off')

    def box(x, y, w, h, text, fc='white', ec=INK2, lw=0.8, fs=7.2):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.2',
            fc=fc, ec=ec, lw=lw))
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
                fontsize=fs, color=INK, linespacing=1.4)

    def arrow(x0, y0, x1, y1):
        ax.add_patch(FancyArrowPatch(
            (x0, y0), (x1, y1), arrowstyle='-|>', mutation_scale=9,
            lw=0.9, color=INK2, shrinkA=1, shrinkB=1))

    box(1, 10, 12.5, 10,
        'raw stream\n$x_t \\in \\mathbb{R}^d$\n(univariate:\n5-axis expansion)',
        fs=6.8)
    box(17, 10, 10.5, 10, 'z-norm on\nclean stats', fs=6.8)
    box(31.5, 16.5, 22, 10.5,
        'regime layer\nGMM, BIC $K$\n+ support floor $\\ell_{floor}$',
        ec=BLUE, lw=1.1, fs=6.8)
    box(31.5, 3, 22, 10.5,
        'six causal scorers\njump · gradual · drift\nrecon · speed · kernel',
        fs=6.8)
    box(57, 10, 19.5, 11,
        'per-regime thresholds\n$T_{k,j}$,  fusion $\\tau_k$\n'
        '(percentiles of own\nclean scores)', fs=6.8)
    box(80.5, 13, 18.5, 14,
        'payload $P_t$\nstate 0 / 1 / 2\nregime · $\\tilde{D}_t$\n'
        'attribution · margin', ec=BLUE, lw=1.1, fs=6.8)
    box(80.5, 1.5, 18.5, 8,
        'downstream policy\ngraded actions (§7)', fs=6.8)

    arrow(13.5, 15, 17, 15)
    arrow(27.5, 15, 31.5, 20.5); arrow(27.5, 15, 31.5, 9)
    arrow(53.5, 21.5, 57, 17.5); arrow(53.5, 8.5, 57, 13)
    arrow(76.5, 15.5, 80.5, 18)
    arrow(89.75, 13, 89.75, 9.5)
    ax.text(42.5, 29.3, 'normal structure  $S$  (construction data only)',
            ha='center', fontsize=7.2, color=INK2, style='italic')
    _save(fig, 'fig1_pipeline')


# ------------------------------------------------------------------ fig2
def fig2():
    """Ghost state: multi-regime support boundary vs single-model T2."""
    from sklearn.mixture import GaussianMixture
    from tests.probes.test_regime_ghost_state import N_CAL, _make_series

    rng = np.random.default_rng(11)
    X, core = _make_series(rng)
    cal = X[:N_CAL]
    Xz = (X - cal.mean(0)) / (cal.std(0) + 1e-12)
    calz, ghost = Xz[:N_CAL], Xz[core]

    gmm = GaussianMixture(2, covariance_type='full', random_state=0).fit(calz)
    lab = gmm.predict(calz)
    ll_cal = gmm.score_samples(calz)
    floor = np.percentile(ll_cal, 0.5)
    iqr = np.subtract(*np.percentile(ll_cal, [75, 25]))
    margin = lambda A: (floor - gmm.score_samples(A)) / abs(iqr)

    mu, cov = calz.mean(0), np.cov(calz.T)
    icov = np.linalg.inv(cov)
    t2 = lambda A: np.einsum('ij,jk,ik->i', A - mu, icov, A - mu)

    fig, (a, b) = plt.subplots(
        1, 2, figsize=(7.0, 2.7), gridspec_kw={'width_ratios': [1.1, 1]})

    for k, c in ((0, BLUE), (1, AQUA)):
        pts = calz[lab == k]
        a.scatter(pts[:, 0], pts[:, 1], s=2.5, c=c, alpha=0.25, lw=0)
        m, C = gmm.means_[k], gmm.covariances_[k]
        w, V = np.linalg.eigh(C)
        ang = np.degrees(np.arctan2(V[1, -1], V[0, -1]))
        for nsig in (2, 3):
            a.add_patch(Ellipse(m, 2 * nsig * np.sqrt(w[-1]),
                                2 * nsig * np.sqrt(w[0]), angle=ang,
                                fc='none', ec=c, lw=0.8, alpha=0.6))
    a.scatter(ghost[:, 0], ghost[:, 1], s=7, c=RED, marker='x', lw=0.7,
              label='ghost fault')
    a.scatter(*calz.mean(0), s=45, c=INK, marker='+', lw=1.2, zorder=4)
    a.annotate('grand mean', calz.mean(0), textcoords='offset points',
               xytext=(-4, -12), fontsize=7, color=INK2, ha='right')
    a.text(gmm.means_[0][0] + 0.35, gmm.means_[0][1], 'regime 1',
           color=BLUE, ha='left', va='center', fontsize=7.5)
    a.text(gmm.means_[1][0] - 0.35, gmm.means_[1][1], 'regime 2',
           color=AQUA, ha='right', va='center', fontsize=7.5)
    ghost_mu = ghost.mean(0)
    a.annotate('ghost (between modes)', ghost_mu,
               textcoords='offset points', xytext=(0, 12),
               fontsize=7.5, color=RED, ha='center')
    a.set_xlabel('load c (z)'); a.set_ylabel('temperature T (z)')
    a.set_title('(a) two regimes, coupling-consistent fault', loc='left')
    a.margins(y=0.14)

    # two stacked hist panels on the right column:
    import matplotlib.gridspec as gs
    b.axis('off')
    sub = gs.GridSpecFromSubplotSpec(2, 1, subplot_spec=b.get_subplotspec(),
                                     hspace=0.75)
    for i, (vc, vg, xlab, note) in enumerate((
            (t2(calz), t2(ghost), 'global $T^2$ (single-model)',
             'ghost median INSIDE the normal bulk — invisible'),
            (margin(calz), margin(ghost), 'unknown-channel margin (IQR)',
             'ghost far beyond the support floor — caught'))):
        axi = fig.add_subplot(sub[i])
        lo = min(vc.min(), vg.min())
        hi = max(np.percentile(vc, 99.9), vg.max())
        bins = np.linspace(lo, hi, 50)
        axi.hist(vc, bins=bins, color=GRID, ec='none', label='calibration')
        axi.hist(vg, bins=bins, color=RED, ec='none', alpha=0.85,
                 label='ghost')
        axi.axvline(np.median(vg), color=RED, lw=1.0, ls='--')
        axi.set_yscale('log'); axi.set_xlabel(xlab, fontsize=7.5)
        axi.set_ylabel('frames', fontsize=7)
        axi.text(0.99, 0.92, note, transform=axi.transAxes, ha='right',
                 va='top', fontsize=6.8, color=INK2, style='italic')
        if i == 0:
            axi.legend(loc='center right', fontsize=7)
            axi.set_title('(b) the same fault, two statistics', loc='left')
    fig.subplots_adjust(wspace=0.28)
    _save(fig, 'fig2_ghost_support')


# ------------------------------------------------------------------ fig3
def fig3():
    """Worked consumer: the margin trajectory grades what BIP saturates."""
    from lambda3_detector.regime import RegimeAwareDetector, \
        expand_anomaly_mask
    from tests.baselines.fgmm_bayes import FGMMBayes
    from tests.probes.test_downstream_policy import (
        DEEP_MARGIN, EVENTS, _episodes, _event_mask, _make_series, _smooth,
        episode_action)

    rng = np.random.default_rng(5)
    X = _make_series(rng)
    mask = _event_mask()
    det = RegimeAwareDetector(K='auto', calibrate_combined=True)
    result = det.fit_predict(X, mask)

    expanded = expand_anomaly_mask(mask, 50)
    ll_clean = result['log_likelihood'][~expanded]
    iqr = float(np.subtract(*np.percentile(ll_clean, [75, 25]))) + 1e-12
    margin = (result['ll_floor'] - result['log_likelihood']) / iqr
    sm = _smooth(margin)

    mu = X[~expanded].mean(axis=0)
    sd = X[~expanded].std(axis=0) + 1e-12
    Xz = (X - mu) / sd
    bip = FGMMBayes().fit(Xz[~expanded]).bip(Xz)

    eps = _episodes(result['state'])
    actions = {ep: episode_action(result, margin, sm, ep) for ep in eps}

    LO, HI = 4400, 7800
    t = np.arange(len(X))
    w = slice(LO, HI)
    ev_info = {
        'E1_transient': ('E1 transient', 'transient\ncheck'),
        'E2_leak': ('E2 leak', 'schedule\nmaintenance'),
        'E3_shallow_ghost': ('E3 shallow ghost', 'reduce &\ninvestigate'),
        'E4_deep_ghost': ('E4 deep ghost', 'stop &\nescalate'),
    }

    fig, (a, b, c) = plt.subplots(
        3, 1, figsize=(7.0, 5.2), sharex=True,
        gridspec_kw={'height_ratios': [1.6, 2.1, 1.1], 'hspace': 0.45})

    a.plot(t[w], X[w, 1], color=BLUE, lw=0.7)
    a.set_ylabel('temperature')
    a.set_title('(a) sensor stream (one of two channels shown)', loc='left')
    for ax in (a, b, c):
        for name, (s, ln) in EVENTS.items():
            ax.axvspan(s, s + ln, color=RED, alpha=0.08, lw=0)
    a.margins(y=0.22)
    for name, (s, ln) in EVENTS.items():
        a.text(s + ln / 2, 0.96, ev_info[name][0], ha='center', va='top',
               fontsize=7, color=INK2,
               transform=a.get_xaxis_transform())

    b.plot(t[w], sm[w], color=BLUE, lw=1.0,
           label='smoothed support margin')
    b.axhline(DEEP_MARGIN, color=INK2, lw=0.8, ls='--')
    b.text(HI - 20, DEEP_MARGIN + 1.2, 'deep threshold (10 IQR, frozen)',
           ha='right', fontsize=7, color=INK2)
    b.axhline(0, color=GRID, lw=0.8)
    b.set_ylabel('margin (cal. IQR)')
    b.set_title('(b) non-saturating unknown margin: '
                'depth and onset slope are the policy inputs', loc='left')
    s3, l3 = EVENTS['E3_shallow_ghost']; s4, l4 = EVENTS['E4_deep_ghost']
    m3 = float(np.median(margin[s3 + 40:s3 + l3]))
    m4 = float(np.median(margin[s4 + 40:s4 + l4]))
    b.annotate(f'depth ≈ {m3:.0f} IQR', (s3 + l3 / 2, m3),
               textcoords='offset points', xytext=(-4, 16), ha='center',
               fontsize=7, color=INK)
    b.annotate(f'depth ≈ {m4:.0f} IQR', (s4 + l4 / 2, m4),
               textcoords='offset points', xytext=(-2, 10), ha='right',
               fontsize=7, color=INK)
    b.legend(loc='upper left')

    c.plot(t[w], bip[w], color=VIOLET, lw=0.5, alpha=0.9,
           label='FGMM-BIP')
    c.set_ylim(-0.05, 1.3)
    c.axhline(1.0, color=GRID, lw=0.8)
    b3 = float(np.median(bip[s3 + 40:s3 + l3]))
    b4 = float(np.median(bip[s4 + 40:s4 + l4]))
    c.annotate(f'{b3:.3f}', (s3 + l3 / 2, 1.0), textcoords='offset points',
               xytext=(0, 6), ha='center', fontsize=7, color=VIOLET)
    c.annotate(f'{b4:.3f}', (s4 + l4 / 2, 1.0), textcoords='offset points',
               xytext=(0, 6), ha='center', fontsize=7, color=VIOLET)
    c.set_ylabel('BIP')
    c.set_xlabel('frame')
    c.set_title('(c) probability-type index: saturated on both ghosts '
                '— a BIP-driven policy cannot grade them', loc='left')
    c.legend(loc='upper left')

    # action labels under panel (c), one per event episode
    for name, (s, ln) in EVENTS.items():
        c.text(s + ln / 2, -0.55, ev_info[name][1], ha='center', va='top',
               fontsize=6.8, color=INK,
               transform=c.get_xaxis_transform())
    a.set_xlim(LO, HI)
    _save(fig, 'fig3_policy_margin')


# ------------------------------------------------------------------ fig4
def fig4():
    """Frozen-config transfer: realized FAR vs designed, detection paired.

    Numbers are the recorded run of tests/multivariate/exp_frozen_transfer.py
    (doc/preregistrations/experiment_plan_multivariate.md A10)."""
    ds = ['rig  d=2', 'SKAB  d=8', 'TEP  d=52']
    xs = np.arange(3)
    series = [  # (label, designed %, realized %, detection %, color, marker)
        ('ours (0.5% floor)', 0.5, [1.06, 0.33, 0.0],
         [100, 57.8, 58.1], BLUE, 'o'),
        ('OC-SVM, γ frozen once', 5.0, [5.19, 21.9, 100.0],
         [100, 80.6, None], RED, 's'),
        ('OC-SVM, γ re-derived', 5.0, [5.12, 4.60, 23.5],
         [100, 68.0, 88.1], ORANGE, '^'),
        ('OC-SVM + our mechanism', 5.0, [5.62, 4.53, 0.0],
         [94.0, 68.3, 0.0], VIOLET, 'D'),
    ]
    off = {-1.5: 0, -0.5: 1, 0.5: 2, 1.5: 3}

    fig, ax = plt.subplots(figsize=(5.4, 3.3))
    ax.set_yscale('symlog', linthresh=0.1)
    ax.axhline(0.5, color=BLUE, lw=0.8, ls=':', alpha=0.7)
    ax.axhline(5.0, color=INK2, lw=0.8, ls=':', alpha=0.7)
    ax.text(2.42, 0.5, 'designed 0.5%', fontsize=6.8, color=BLUE,
            va='bottom', ha='right')
    ax.text(2.42, 5.0, 'designed 5%', fontsize=6.8, color=INK2,
            va='bottom', ha='right')

    # per-point detection labels only where methods separate (d=8, d=52);
    # at d=2 all four sit at their designed rates — one shared note.
    stagger = {RED: (0, 9), ORANGE: (0, 9), VIOLET: (8, -13),
               BLUE: (0, -13)}
    for i, (lab, des, far, det, col, mk) in enumerate(series):
        x = xs + (i - 1.5) * 0.09
        ax.plot(x, far, color=col, lw=1.2, alpha=0.8, zorder=2)
        ax.scatter(x, far, s=26, color=col, marker=mk, zorder=3, label=lab)
        for xi, fi, di in list(zip(x, far, det))[1:]:
            txt = 'flags everything' if di is None else f'det {di:.0f}%'
            dx, dy = stagger[col]
            ax.annotate(txt, (xi, fi), textcoords='offset points',
                        xytext=(dx, dy), ha='center', fontsize=6.2,
                        color=col)
    ax.text(-0.13, 0.16, 'all methods at\ndesign rate here\n(det 94–100%)',
            fontsize=6.2, color=INK2, ha='left')
    ax.set_xticks(xs); ax.set_xticklabels(ds)
    ax.set_ylabel('realized clean flag rate (%)  [symlog]')
    ax.set_ylim(-0.05, 400)
    ax.set_yticks([0, 0.1, 0.5, 1, 5, 10, 100])
    ax.set_yticklabels(['0', '0.1', '0.5', '1', '5', '10', '100'])
    ax.grid(axis='y', alpha=0.5)
    ax.set_title('operating point fixed once, evaluated held-out — '
                 'FAR always paired with detection', loc='left',
                 fontsize=8)
    ax.legend(loc='upper left', ncol=1, handletextpad=0.4)
    _save(fig, 'fig4_frozen_transfer')


# ------------------------------------------------------------------ fig5
def fig5():
    """Mode A/B: per-file sweep separability is bimodal (52 NAB files)."""
    from tests.nab.benchmark_nab_corpus import _key, load_cache, load_corpus
    from tests.nab.nab_metrics import score_with_sweeper

    cache = load_cache('nab_score_cache', 'lambda3_tier2_cal')
    scores = {}
    for s in load_corpus(include_empty=False):
        best = score_with_sweeper(s, cache[_key(s.name)]).normalized
        scores[s.name] = best
    vals = np.array(list(scores.values()))

    fig, ax = plt.subplots(figsize=(5.2, 2.6))
    bins = np.arange(-2.5, 101, 5)
    ax.hist(vals, bins=bins, color=BLUE, ec='white', lw=0.5)
    ax.set_xlabel('per-file sweep separability (diagnostic protocol P2)')
    ax.set_ylabel('files')
    ax.grid(axis='y', alpha=0.5)
    med_a = np.median(vals[vals > 50])
    ax.text(med_a, ax.get_ylim()[1] * 0.95,
            'Mode A — regimes covered', ha='center', va='top',
            fontsize=7.5, color=INK)
    ax.text(2, ax.get_ylim()[1] * 0.95,
            'Mode B — normal structure\nviolated (B1–B4)', ha='left',
            va='top', fontsize=7.5, color=INK)
    nB = int((vals < 30).sum())
    ax.set_title(f'(52 labeled files; {nB} files below 30 — each a named '
                 'structural cause, §7.1)', loc='left', fontsize=8)
    _save(fig, 'fig5_mode_ab')
    lo = sorted(scores.items(), key=lambda kv: kv[1])[:8]
    for k, v in lo:
        print(f'    low file: {v:7.2f}  {k}')


ALL = {'fig1': fig1, 'fig2': fig2, 'fig3': fig3, 'fig4': fig4, 'fig5': fig5}

if __name__ == '__main__':
    which = sys.argv[1:] or list(ALL)
    for name in which:
        print(f'[{name}]')
        ALL[name]()
