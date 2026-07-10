"""The worked downstream consumer — the demo the interpretation-layer
claim stands on.

A small rule-based policy consumes the interpretation payload — three-
state channel, per-scorer attribution, and the NON-SATURATING unknown
margin (including its own trajectory) — and emits graded actions on a
bimodal rig with four events:

  E1 fast transient   in-support T-spike (mode B)     -> L1 transient check
  E2 slow leak        gradual egress out of support   -> L1 schedule maintenance
  E3 shallow ghost    abrupt egress, mild depth       -> L2 reduce & investigate
  E4 deep ghost       abrupt egress, valley center    -> L3 stop & escalate

Decisive contrasts:
  (1) E3 vs E4 — the non-saturating margin grades depth; FGMM-BIP
      saturates at ~1.0 on both, so any BIP-driven policy is forced to
      give the two ghosts the same action.
  (2) E2 vs E3 — HOW the process left normal structure is read from the
      margin trajectory itself: a leak egresses gradually (smoothed
      onset slope << 1 IQR/frame), a ghost abruptly. No extra detector
      machinery — the payload already contains it.

Actions are assigned per EPISODE (contiguous non-normal run, gaps <= 3
frames bridged) — the unit a real consumer acts on.

Structural defaults, frozen (not tuned to the demo): unknown floor
0.5%; DEEP_MARGIN = 10 calibration-IQR; ONSET_SLOPE = 1 IQR/frame on
a 5-frame-smoothed margin; scorer taxonomy fast/slow by temporal
character. Rig geometry (event placement/amplitude) is the experimental
design; the detector config is the NAB-frozen one, untouched.
"""

import numpy as np
import pytest

from lambda3_detector.regime import RegimeAwareDetector, expand_anomaly_mask
from tests.baselines.fgmm_bayes import FGMMBayes

N_CAL = 4000
N = 8000
MODE_LEN = 800
TAU_T = 25.0
NOISE_C = 0.02
NOISE_T = 0.4
WANDER_AMP = 2.0
WANDER_PERIOD = 600

DEEP_MARGIN = 10.0      # L3 above this many calibration-IQRs past the floor
ONSET_SLOPE = 1.0       # IQR/frame on smoothed margin: gradual vs abrupt egress
EPISODE_GAP = 3

EVENTS = {
    'E1_transient': (4650, 12),
    'E2_leak': (5700, 100),
    'E3_shallow_ghost': (6100, 150),
    'E4_deep_ghost': (7400, 150),
}
GHOST_SHALLOW_C = 0.615
GHOST_DEEP_C = 0.50

L0, L1T, L1M, L2, L3 = ('L0_continue', 'L1_transient_check',
                        'L1_schedule_maintenance',
                        'L2_reduce_investigate', 'L3_stop_escalate')

FAST = {'StreamingJumpScorer', 'StreamingReconstructionScorer',
        'StreamingKernelScorer', 'StreamingStructuralScorer'}
SLOW = {'StreamingGradualScorer', 'StreamingStructuralDriftScorer'}


def _make_series(rng):
    t = np.arange(N)
    mode = (t // MODE_LEN) % 2
    c_target = np.where(mode == 0, 0.3, 0.7).astype(np.float64)

    s, ln = EVENTS['E3_shallow_ghost']
    c_target[s:s + ln] = GHOST_SHALLOW_C
    s, ln = EVENTS['E4_deep_ghost']
    c_target[s:s + ln] = GHOST_DEEP_C

    # load switches are instantaneous (commanded steps): the inter-mode
    # c-valley stays EMPTY of normal data; the thermal relaxation after
    # each switch is a normal off-coupling corridor along T
    c = c_target + NOISE_C * rng.normal(size=N)
    T = np.zeros(N)
    T[0] = 20.0 + 40.0 * c[0]
    for i in range(1, N):
        T_ss = 20.0 + 40.0 * c[i]
        T[i] = T[i - 1] + (T_ss - T[i - 1]) / TAU_T
    T = T + WANDER_AMP * np.sin(2 * np.pi * t / WANDER_PERIOD) \
        + NOISE_T * rng.normal(size=N)

    s, ln = EVENTS['E1_transient']
    T[s:s + 4] += 3.0                          # fast in-support spike
    s, ln = EVENTS['E2_leak']
    # slow leak upward, out the top of the support (above both the mode-B
    # cloud and the relaxation corridor), at ~10x wander slope but far
    # below relaxation slopes
    T[s:s + ln] += np.concatenate(
        [np.linspace(0.0, 6.5, 90), np.full(ln - 90, 6.5)])
    return np.column_stack([c, T])


def _event_mask():
    m = np.zeros(N, dtype=bool)
    for s, ln in EVENTS.values():
        m[s:s + ln] = True
    return m


def _episodes(state):
    """Contiguous non-normal runs, bridging gaps <= EPISODE_GAP."""
    idx = np.where(state != 0)[0]
    eps = []
    for t in idx:
        if eps and t - eps[-1][-1] <= EPISODE_GAP + 1:
            eps[-1].append(t)
        else:
            eps.append([t])
    return [(e[0], e[-1]) for e in eps]


def _smooth(x, w=5):
    return np.convolve(x, np.ones(w) / w, mode='same')


def egress_onset_slope(sm_margin, a, window=30, span=5):
    """Max span-frame average slope of the smoothed margin around an
    egress onset at frame a: ghosts step (>= ~1 IQR/frame), leaks creep
    (~0.1); single-frame diffs would sit at the noise floor."""
    lo = max(span, a - 2)
    ts = range(lo, min(len(sm_margin), a + window))
    return max((sm_margin[t] - sm_margin[t - span]) / span for t in ts)


def _dominant(result, t):
    k = int(result['regimes'][t])
    best, best_ratio = None, -1.0
    for name, raw in result['per_scorer'].items():
        thr = result['thresholds_per_regime'][k].get(name, float('inf'))
        if np.isfinite(thr) and thr > 0 and raw[t] / thr > best_ratio:
            best, best_ratio = name, raw[t] / thr
    return best


def episode_action(result, margin, sm_margin, ep):
    """The downstream consumer: one graded action per episode."""
    a, b = ep
    frames = range(a, b + 1)
    has_unknown = (result['state'][a:b + 1] == 2).any()
    if has_unknown:
        # depth on the smoothed margin: a 1-2 frame noise spike must not
        # trigger an emergency stop
        if sm_margin[a:b + 1].max() > DEEP_MARGIN:
            return L3
        # HOW did it leave normal structure? gradual egress = wear/leak
        slope = egress_onset_slope(sm_margin, a)
        return L1M if slope < ONSET_SLOPE else L2
    doms = [_dominant(result, t) for t in frames
            if result['state'][t] == 1]
    n_slow = sum(d in SLOW for d in doms)
    return L1M if n_slow > len(doms) / 2 else L1T


@pytest.fixture(scope='module')
def rig():
    rng = np.random.default_rng(5)
    X = _make_series(rng)
    mask = _event_mask()
    det = RegimeAwareDetector(K='auto', calibrate_combined=True)
    result = det.fit_predict(X, mask)

    expanded = expand_anomaly_mask(mask, 50)
    ll_clean = result['log_likelihood'][~expanded]
    iqr = float(np.subtract(*np.percentile(ll_clean, [75, 25]))) + 1e-12
    margin = (result['ll_floor'] - result['log_likelihood']) / iqr
    sm_margin = _smooth(margin)

    mu = X[~expanded].mean(axis=0)
    sd = X[~expanded].std(axis=0) + 1e-12
    Xz = (X - mu) / sd
    fg = FGMMBayes().fit(Xz[~expanded])     # fair: same z-space
    bip = fg.bip(Xz)

    eps = _episodes(result['state'])
    actions = {ep: episode_action(result, margin, sm_margin, ep)
               for ep in eps}
    return X, result, margin, sm_margin, bip, eps, actions


def _event_episode_action(eps, actions, name, min_overlap=10):
    s, ln = EVENTS[name]
    best, best_ov = None, 0
    for ep, act in actions.items():
        ov = max(0, min(ep[1], s + ln - 1) - max(ep[0], s) + 1)
        if ov > best_ov:
            best, best_ov = act, ov
    assert best is not None and best_ov >= min(min_overlap, ln // 2), (
        f"{name}: no episode overlaps the event (best overlap {best_ov})"
    )
    return best


def test_event_actions(rig):
    X, result, margin, sm, bip, eps, actions = rig
    assert _event_episode_action(eps, actions, 'E1_transient',
                                 min_overlap=4) == L1T
    assert _event_episode_action(eps, actions, 'E2_leak') == L1M
    assert _event_episode_action(eps, actions, 'E3_shallow_ghost') == L2
    assert _event_episode_action(eps, actions, 'E4_deep_ghost') == L3


def test_bip_cannot_grade_the_ghosts(rig):
    """BIP saturates on both ghosts -> any BIP-driven policy gives E3 and
    E4 the same action; the non-saturating margin separates them."""
    X, result, margin, sm, bip, eps, actions = rig
    s3, l3_ = EVENTS['E3_shallow_ghost']
    s4, l4_ = EVENTS['E4_deep_ghost']
    core3, core4 = slice(s3 + 40, s3 + l3_), slice(s4 + 40, s4 + l4_)
    b3, b4 = float(np.median(bip[core3])), float(np.median(bip[core4]))
    assert b3 > 0.99 and b4 > 0.99, (b3, b4)
    assert abs(b4 - b3) < 0.02, "BIP unexpectedly separates the ghosts"
    m3, m4 = float(np.median(margin[core3])), float(np.median(margin[core4]))
    assert m4 > 3 * max(m3, 1e-9), (m3, m4)
    assert m3 < DEEP_MARGIN < m4, (m3, m4)


def test_leak_vs_ghost_egress_signature(rig):
    """The margin trajectory distinguishes gradual egress (leak) from
    abrupt egress (ghost) — payload-only, no extra detector machinery."""
    X, result, margin, sm, bip, eps, actions = rig

    def onset_slope(name):
        s, ln = EVENTS[name]
        # anchor at the first out-of-support frame within the event
        egress = np.where(result['state'][s:s + ln] == 2)[0]
        a = s + (int(egress[0]) if len(egress) else 0)
        return float(egress_onset_slope(sm, a))

    leak = onset_slope('E2_leak')
    g3 = onset_slope('E3_shallow_ghost')
    g4 = onset_slope('E4_deep_ghost')
    assert leak < ONSET_SLOPE, f"leak egress not gradual: {leak:.2f}"
    assert g3 > ONSET_SLOPE and g4 > ONSET_SLOPE, (g3, g4)


def test_quiet_on_normal_frames(rig):
    X, result, margin, sm, bip, eps, actions = rig
    expanded = expand_anomaly_mask(_event_mask(), 60)
    flagged = np.zeros(N, dtype=bool)
    for (a, b), act in actions.items():
        if act != L0:
            flagged[a:b + 1] = True
    normal_test = [t for t in range(N_CAL, N) if not expanded[t]]
    rate = flagged[normal_test].mean()
    assert rate < 0.03, f"policy noisy on normal frames: {rate:.2%}"
