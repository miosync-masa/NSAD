"""Generate the v2 manuscript figures (doc/paper/paper_v2_outline.md §5).

Publication build step: reads ONLY the machine-readable snapshot in
paper_results/ (produced by tests/figures/export_paper_results.py) —
no dataset access, no experiment code, no hand-typed numbers. The v1
generator (make_figures.py) is untouched and keeps producing the
Appendix figures fig1–fig5.

  v2_fig1  Paderborn severity ladders: per-bearing median margin vs
           physical damage extent (inner / outer real pitting)
  v2_fig2  The dilemma panel: unseen-healthy FAR vs extent-1
           absorption for support-widening candidates (#2 A–D, killed)
           against commissioning (#2 E, #3 E3)
  v2_fig3  IMS run-to-failure: per-asset margin trajectories with
           sustained onset vs the E3 fleet margin (late or silent)
  v2_fig4  Three-layer deployment schematic (no data)
  v2_fig5  Hydraulic graded severity: per-stage margin distributions
           across the five registered splits (cooler / valve)

Colors are the validated reference categorical palette shared with
make_figures.py; killed/supported use RED/BLUE with direct labels on
every mark (identity never color-alone).

Usage::
    python -m tests.figures.make_paper_v2_figures            # all
    python -m tests.figures.make_paper_v2_figures fig2 fig5  # subset
"""

from __future__ import annotations

import json
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

RES = os.path.join(os.path.dirname(__file__), '..', '..', 'paper_results')
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


def _csv(name):
    return pd.read_csv(os.path.join(RES, name))


# ------------------------------------------------------------------ v2_fig1
def fig1():
    """Severity ladders: median margin vs physical extent (#1)."""
    df = _csv('paderborn_severity.csv')
    df = df[df.condition == 'all']
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.6), sharey=False)
    panels = [('inner ring — real fatigue pitting', 'inner',
               ['KI04', 'KI14', 'KI17', 'KI21', 'KI18', 'KI16']),
              ('outer ring — real fatigue pitting', 'outer',
               ['KA04', 'KA22', 'KA16'])]
    healthy = df[df.extent == 0]
    for ax, (title, ring, bearings) in zip(axes, panels):
        sub = df[df.bearing.isin(bearings)]
        # healthy reference band (extent 0): identity spread of the
        # six healthy bearings under the same primary model
        ax.axhspan(healthy.median_margin.min(),
                   healthy.median_margin.max(), color=GRID, alpha=0.5,
                   lw=0, zorder=0)
        ax.axhline(0, color=INK2, lw=0.6, ls=':')
        jit = {1: -0.06, 2: 0.0, 3: 0.06}
        for _, r in sub.iterrows():
            x = r.extent + jit.get(r.extent, 0) * (
                hash(r.bearing) % 5 - 2)
            ax.plot([x], [r.median_margin], 'o', ms=4.5, color=BLUE,
                    mec='white', mew=0.5, zorder=3)
            ax.annotate(r.bearing, (x, r.median_margin),
                        textcoords='offset points', xytext=(5, -2),
                        fontsize=6.2, color=INK2)
        med = sub.groupby('extent').median_margin.median()
        ax.plot(med.index, med.values, '-', color=BLUE, lw=2,
                alpha=0.55, zorder=2)
        ax.set_title(title, loc='left')
        ax.set_xlabel('physical damage extent (fact sheets)')
        ax.set_xticks(sorted(sub.extent.unique()))
        ax.grid(True, axis='y')
        ax.set_axisbelow(True)
    axes[0].set_ylabel('median severity margin (IQR units)')
    axes[0].text(1.0, healthy.median_margin.max(), ' healthy identity band',
                 fontsize=6.2, color=INK2, va='bottom')
    _save(fig, 'v2_fig1_severity_ladder')


# ------------------------------------------------------------------ v2_fig2
def fig2():
    """The dilemma: FAR vs extent-1 absorption; widening vs commissioning."""
    sup = _csv('paderborn_support_candidates.csv')
    com = _csv('paderborn_commissioning.csv')
    fig, ax = plt.subplots(figsize=(4.6, 3.0))
    # severity-side absorption is 11.9% for the shared geometry; the
    # E-family's alarm-side damage values equal it (registered
    # disclosure: damaged units carry no commissioning).
    sev_absorb = float(sup[sup.candidate.str.startswith('A')]
                       .absorb_e1.iloc[0])
    killed = sup[~sup.candidate.str.startswith('E')]
    for _, r in killed.iterrows():
        ax.plot(100 * r.far_mean, 100 * r.absorb_e1, 'o', ms=6,
                color=RED, mec='white', mew=0.6, zorder=3)
        ax.annotate(r.candidate.split()[0], (100 * r.far_mean,
                                             100 * r.absorb_e1),
                    textcoords='offset points', xytext=(6, 3),
                    fontsize=7, color=INK)
    e2 = sup[sup.candidate.str.startswith('E')].iloc[0]
    e3 = com[com.configuration == 'E3 loc+scale n=4'].iloc[0]
    for far, name in ((e2.far_mean, 'E (#2, one scalar)'),
                      (e3.far_mean, 'E3 (#3, loc+scale)')):
        ax.plot(100 * far, 100 * sev_absorb, 'D', ms=6, color=BLUE,
                mec='white', mew=0.6, zorder=3)
        ax.annotate(name, (100 * far, 100 * sev_absorb),
                    textcoords='offset points', xytext=(6, -9),
                    fontsize=7, color=INK)
    ax.axvline(0.5, color=INK2, lw=0.7, ls='--')
    ax.text(0.5, 44, ' designed FAR 0.5%', fontsize=6.5, color=INK2,
            rotation=90, va='top')
    ax.axhline(100 * sev_absorb, color=GRID, lw=0.8)
    ax.text(0.115, 100 * sev_absorb + 1, 'severity-side absorption '
            '(bit-identical for the E family)', fontsize=6.2,
            color=INK2)
    ax.set_xscale('log')
    ax.set_xlim(0.08, 80)
    ax.set_ylim(0, 48)
    ax.set_xlabel('unseen-healthy FAR, mean over folds (%)  [log]')
    ax.set_ylabel('extent-1 damage absorbed (%)')
    ax.set_title('support widening (killed) vs commissioning '
                 '(alarm-side only)', loc='left')
    ax.grid(True, which='both', axis='x')
    ax.set_axisbelow(True)
    _save(fig, 'v2_fig2_dilemma')


# ------------------------------------------------------------------ v2_fig3
def fig3():
    """IMS: per-asset margin trajectories, onset, and the E3 fleet margin."""
    z = np.load(os.path.join(RES, 'ims_trajectories.npz'))
    s = _csv('ims_summary.csv')
    cases = [('test1', 3, 'IMS test 1 — bearing 3 (inner race)'),
             ('test1', 4, 'IMS test 1 — bearing 4 (roller)'),
             ('test2', 1, 'IMS test 2 — bearing 1 (outer race)')]
    fig, axes = plt.subplots(3, 1, figsize=(6.8, 5.4), sharex=True)
    for ax, (test, b, title) in zip(axes, cases):
        med = z[f'med_{test}_b{b}']
        e3 = z[f'e3med_{test}_b{b}']
        n = len(med)
        life = 100 * np.arange(n) / n
        row = s[(s.test == test) & (s.bearing == b)].iloc[0]
        n_con = int(z[f'ncon_{test}_b{b}'])
        ax.axvspan(0, 100 * n_con / n, color=GRID, alpha=0.5, lw=0)
        ax.axhline(0, color=INK2, lw=0.6, ls=':')
        ax.plot(life, np.clip(e3, -20, None), lw=0.9, color=RED,
                alpha=0.8, label='E3 fleet margin (H3L)')
        ax.plot(life, np.clip(med, -20, None), lw=1.1, color=BLUE,
                label='per-asset margin')
        ax.set_yscale('symlog', linthresh=5)
        ax.set_xlim(-1, 101)
        ylo, yhi = ax.get_ylim()
        onset = row.onset_pct
        ax.axvline(onset, color=BLUE, lw=1.0)
        ax.annotate(f'onset {onset:.0f}% (lead {row.lead_h:.0f} h, '
                    f'persist {100 * row.persistence:.1f}%) ',
                    (onset, yhi), textcoords='offset points',
                    xytext=(-4, -9), fontsize=6.5, color=BLUE,
                    ha='right', va='top')
        if np.isfinite(row.e3_onset_pct):
            ax.axvline(row.e3_onset_pct, color=RED, lw=1.0, ls='--')
            side = 'right' if row.e3_onset_pct > 80 else 'left'
            dx = -4 if side == 'right' else 4
            ax.annotate(f'E3 onset {row.e3_onset_pct:.0f}% '
                        f'(+{row.e3_delay_pct:.1f}% of life late)',
                        (row.e3_onset_pct, yhi),
                        textcoords='offset points', xytext=(dx, -21),
                        fontsize=6.5, color=RED, ha=side, va='top')
        else:
            ax.annotate('E3: no sustained onset (silent)', (100, yhi),
                        textcoords='offset points', xytext=(-4, -21),
                        fontsize=6.8, color=RED, ha='right', va='top')
        ax.text(1.2, ylo * 0.55, 'construction\n(first 20%)',
                fontsize=6.2, color=INK2, va='bottom')
        ax.set_title(title, loc='left')
        ax.set_ylabel('margin (IQR)')
        ax.grid(True, axis='y')
        ax.set_axisbelow(True)
    axes[0].legend(loc='center left', ncol=1, borderaxespad=1.2)
    axes[-1].set_xlabel('life (%)')
    _save(fig, 'v2_fig3_ims_longitudinal')


# ------------------------------------------------------------------ v2_fig4
def fig4():
    """Three-layer deployment schematic: fleet -> commissioning -> asset."""
    fig, ax = plt.subplots(figsize=(7.0, 2.5))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 30)
    ax.axis('off')

    def box(x, y, w, h, text, ec=INK2, lw=0.9, fs=6.8, fc='white'):
        ax.add_patch(FancyBboxPatch(
            (x, y), w, h, boxstyle='round,pad=0.6,rounding_size=1.2',
            fc=fc, ec=ec, lw=lw))
        ax.text(x + w / 2, y + h / 2, text, ha='center', va='center',
                fontsize=fs, color=INK, linespacing=1.5)

    def arrow(x0, y0, x1, y1, text='', color=INK2):
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1),
                                     arrowstyle='-|>', mutation_scale=10,
                                     lw=1.0, color=color))
        if text:
            ax.text((x0 + x1) / 2, (y0 + y1) / 2 + 1.6, text,
                    ha='center', fontsize=6.2, color=color)

    box(1, 6, 28, 19,
        'FACTORY-SHARED\n(fleet prior)\n\nfault-agnostic adapter\n'
        'shared geometry · severity margin\nthe common ruler\n'
        '#1: ordering 12/12, ρ +0.85/+0.87', ec=BLUE, lw=1.2, fs=6.3)
    box(36, 6, 28, 19,
        'COMMISSIONING\n(admission)\n\nhealthy median + IQR (~64 s)\n'
        'alarm origin + unit, per asset\n#3: FAR 0.10%, severity '
        'bit-identical\nNEVER the failure alarm (#4 H3L)', ec=AQUA,
        lw=1.2, fs=6.3)
    box(71, 6, 28, 19,
        'IN SERVICE\n(asset posterior)\n\nown-history longitudinal\n'
        'reference: onset · occupancy ·\ndeepening   #4: lead '
        '74–148 h,\npersistence 93.5–99.6%', ec=VIOLET, lw=1.2,
        fs=6.3)
    arrow(29.6, 15.5, 35.4, 15.5)
    ax.text(32.5, 18.2, 'new\nunit', ha='center', fontsize=6.0,
            color=INK2)
    arrow(64.6, 15.5, 70.4, 15.5)
    ax.text(67.5, 18.2, 'history\naccumulates', ha='center',
            fontsize=6.0, color=INK2)
    ax.text(50, 1.2, 'share the geometry — commission the individual — '
            'monitor degradation against its own history',
            ha='center', fontsize=7.2, color=INK2, style='italic')
    _save(fig, 'v2_fig4_deployment')


# ------------------------------------------------------------------ v2_fig5
def fig5():
    """Hydraulic graded severity across the five registered splits (#5)."""
    df = _csv('hydraulic_seed_stage.csv')
    fig, axes = plt.subplots(1, 2, figsize=(6.8, 2.7))
    panels = [('cooler — magnitude profile', 'cooler',
               {20.0: 'stage 20%', 3.0: 'stage 3%'}, 'symlog'),
              ('valve — timing geometry', 'valve',
               {90.0: '90%', 80.0: '80%', 73.0: '73%'}, 'linear')]
    for ax, (title, target, stages, yscale) in zip(axes, panels):
        sub = df[df.target == target]
        for si, (stage, label) in enumerate(stages.items()):
            g = sub[sub.stage == stage]
            for k, (_, r) in enumerate(g.iterrows()):
                x = si + (k - 2) * 0.09
                ax.plot([x, x], [r.p25, r.p75], lw=1.6, color=BLUE,
                        alpha=0.75, solid_capstyle='round')
                ax.plot([x], [r['median']], 'o', ms=3.4, color=BLUE,
                        mec='white', mew=0.4)
            ax.annotate(f'det {100 * g.det.mean():.0f}%',
                        (si, g.p95.max()), textcoords='offset points',
                        xytext=(0, 7), ha='center', fontsize=6.5,
                        color=INK2)
        ax.axhline(0, color=INK2, lw=0.7, ls='--')
        if yscale == 'symlog':
            ax.set_yscale('symlog', linthresh=10)
        ax.set_xlim(-0.55, len(stages) - 0.45)
        ax.margins(y=0.14)
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages.values())
        ax.set_title(title, loc='left')
        ax.set_xlabel('degradation stage (mild → severe)')
        ax.grid(True, axis='y')
        ax.set_axisbelow(True)
    axes[0].set_ylabel('margin (IQR), 5 registered splits')
    axes[1].annotate('alarm floor', (len(panels[1][2]) - 1.42, 0),
                     fontsize=6.2, color=INK2, va='bottom',
                     ha='left')
    _save(fig, 'v2_fig5_hydraulic')


FIGS = dict(fig1=fig1, fig2=fig2, fig3=fig3, fig4=fig4, fig5=fig5)


def main(argv):
    manifest = os.path.join(RES, 'manifest.json')
    if os.path.exists(manifest):
        with open(manifest) as fh:
            m = json.load(fh)
        print(f"paper_results snapshot: export commit "
              f"{m.get('export_commit', '?')[:8]}, verification "
              f"{'ALL MATCH' if m.get('verification_all_match') else 'MISMATCHES PRESENT'}")
    wanted = argv or list(FIGS)
    for name in wanted:
        FIGS[name]()


if __name__ == '__main__':
    main(sys.argv[1:])
