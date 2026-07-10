"""Mechanism probe (GATE) — doc/preregistrations/experiment_plan_multivariate.md §9 Step 1.

Thesis in one test: a coordination break between two coupled channels
(current ↔ temperature) where BOTH marginals stay well inside their normal
bands is (a) certified contextual, (b) invisible to per-channel marginal
detection (V0 proxy = StreamingJumpScorer per channel), and (c) caught by
the joint delay-embedded reconstruction residual (V2 =
StreamingReconstructionScorer with d=2).

Break design — *anti-phase coupling for one half-cycle*: during the
break, temperature tracks the load of half a period ago with slightly
damped gain, `T = f(0.5 + 0.8·(c(t-250) − 0.5))`, instead of `T = f(c(t))`
(physically: a degraded/inverted cooling response). The break starts and
ends exactly at zero phase-offset (sine zero crossings), so T is
*continuous with continuous-magnitude velocity at both boundaries* — no
blend edges, no marginal transient. Every T value during the break is a
mid-range ordinary temperature moving at an ordinary rate; every c value
is untouched; only the *pairing* is wrong. This is the purest form of a
contextual anomaly.

V0 semantics: a per-channel p99-calibrated scorer flags ~1% of NORMAL
frames by construction, and those flags are *phase-clustered* (fast-slope
frames dominate the p99 tail). "Misses" is therefore asserted against
matched-phase control windows (same cycle position, ±1 period, both
normal) — not against the all-phase average and not as zero flags.

Pre-registered discipline: if the joint residual does NOT fire here,
the multivariate extension stops (do not proceed to SKAB/TEP).
"""

import numpy as np
import pytest

from lambda3_detector.streaming import (
    StreamingJumpScorer,
    StreamingReconstructionScorer,
)

N_CAL = 3000
N_TEST = 1500
PERIOD = 500           # load cycle length (frames)
LAG = 250              # half period (anti-phase) — the break's phase shift;
                       # keeps T mid-range while the pairing inverts
GAIN_BREAK = 0.8       # damped break gain: keeps T_break clear of the
                       # marginal band edge (max ≈ 48 vs band hi ≈ 51)
NOISE_C = 0.02
NOISE_T = 0.5
BREAK_START = 3750     # sine zero crossing (phase π): zero offset at entry
BREAK_LEN = 250        # one half-cycle: zero offset again at exit


def _make_series(rng):
    n = N_CAL + N_TEST
    t = np.arange(n)
    c = 0.5 + 0.25 * np.sin(2 * np.pi * t / PERIOD) + NOISE_C * rng.normal(size=n)
    c_lag = 0.5 + 0.25 * np.sin(2 * np.pi * (t - LAG) / PERIOD) \
        + NOISE_C * rng.normal(size=n)
    T_normal = 20.0 + 40.0 * c + NOISE_T * rng.normal(size=n)
    T_break = 20.0 + 40.0 * (0.5 + GAIN_BREAK * (c_lag - 0.5)) \
        + NOISE_T * rng.normal(size=n)

    # break = one half-cycle of anti-phase coupling, seamless at both ends
    # (offset is zero at the sine zero crossings that bound the break)
    w = np.zeros(n)
    s = BREAK_START
    w[s:s + BREAK_LEN] = 1.0

    T = (1.0 - w) * T_normal + w * T_break
    X = np.column_stack([c, T])
    core = slice(s + 50, s + BREAK_LEN - 50)   # strong-contrast frames
    event = slice(s, s + BREAK_LEN)            # full break
    return X, core, event


@pytest.fixture(scope='module')
def probe():
    rng = np.random.default_rng(42)
    X, core, event = _make_series(rng)
    cal = X[:N_CAL]
    mu, sd = cal.mean(axis=0), cal.std(axis=0) + 1e-12
    Xz = (X - mu) / sd                     # per-channel z-norm (guardrail)
    return X, Xz, core, event


def _jump_ratios(Xz, ch, frames):
    x1 = Xz[:, ch:ch + 1]
    s = StreamingJumpScorer(percentile=99.0)
    s.calibrate(x1[:N_CAL])
    return np.array([s.score(x1, t) / (s.threshold + 1e-12) for t in frames])


def _recon_ratios(Xz, frames):
    s = StreamingReconstructionScorer(n_components=5, delay_window=20)
    s.calibrate(Xz[:N_CAL])
    return np.array([s.score(Xz, t) / (s.threshold + 1e-12) for t in frames])


def _normal_test_frames(event, margin=20):
    return [t for t in range(N_CAL, N_CAL + N_TEST)
            if t < event.start or t >= event.stop + margin]


def test_break_is_contextual(probe):
    """Both marginals stay inside the clean quantile band during the break
    at chance level (refined §4 tagging rule).

    Refinement discovered by this probe: with a [0.5%, 99.5%] band, ~1% of
    frames of a *fully normal* window sit outside the band by construction,
    so "any frame exits" would mis-tag long normal-marginal events as
    univariate. An event counts as univariate only if a channel exits its
    band *beyond chance*: out-of-band fraction > 2× the nominal tail rate,
    or a sustained run (≥5 consecutive frames) outside the band.
    """
    X, _, _, event = probe
    cal = X[:N_CAL]
    lo = np.quantile(cal, 0.005, axis=0)
    hi = np.quantile(cal, 0.995, axis=0)
    nominal_tail = 0.01           # two-sided mass outside the band
    seg = X[event]
    for ch, name in [(0, 'current'), (1, 'temperature')]:
        out = (seg[:, ch] < lo[ch]) | (seg[:, ch] > hi[ch])
        assert out.mean() <= 2 * nominal_tail, (
            f"{name}: out-of-band fraction {out.mean():.3f} exceeds chance "
            f"— event would be univariate, probe is misconstructed"
        )
        # no sustained excursion (runs of >=5 consecutive out-of-band frames)
        run, longest = 0, 0
        for o in out:
            run = run + 1 if o else 0
            longest = max(longest, run)
        assert longest < 5, (
            f"{name}: sustained marginal excursion ({longest} consecutive "
            f"frames out of band) — event would be univariate"
        )


def test_v0_marginal_detection_misses(probe):
    """Per-channel jump detection (V0 proxy) stays at the matched-phase
    background flag rate during the break — no marginal signal."""
    _, Xz, _, event = probe
    # matched-phase controls: same cycle position, one period before/after,
    # both fully normal and inside the test segment
    controls = [range(event.start - PERIOD, event.stop - PERIOD),
                range(event.start + PERIOD, event.stop + PERIOD)]
    for ch in (0, 1):
        event_rate = (_jump_ratios(
            Xz, ch, range(event.start, event.stop)) >= 1.0).mean()
        control_rate = np.mean([
            (_jump_ratios(Xz, ch, ctrl) >= 1.0).mean() for ctrl in controls
        ])
        assert event_rate <= control_rate + 0.05, (
            f"channel {ch}: marginal detector elevated during break "
            f"(event {event_rate:.3f} vs matched-phase control "
            f"{control_rate:.3f})"
        )


def test_v2_joint_residual_fires(probe):
    """Joint delay-embedded reconstruction residual fires during the break."""
    _, Xz, core, _ = probe
    ratios = _recon_ratios(Xz, range(core.start, core.stop))
    assert ratios.max() > 1.5, (
        f"GATE FAILED: joint residual did not fire on the coordination "
        f"break (max ratio {ratios.max():.2f}) — stop, do not proceed"
    )
    # sustained catch, not one fluke frame
    assert (ratios >= 1.0).mean() > 0.5, (
        f"joint residual fired only sporadically "
        f"({(ratios >= 1.0).mean():.0%} of core frames)"
    )


def test_v2_quiet_on_normal_frames(probe):
    """The joint residual fires *specifically*: low flag rate elsewhere."""
    _, Xz, _, event = probe
    ratios = _recon_ratios(Xz, _normal_test_frames(event))
    flag_rate = (ratios >= 1.0).mean()
    assert flag_rate < 0.03, (
        f"joint residual too noisy on normal frames (flag rate "
        f"{flag_rate:.3%}) — not a usable detector"
    )
