"""Per-unit healthy commissioning (location + scale) — E3 of
pre-registration #3, promoted with its measured role boundary.

ROLE BOUNDARY (load-bearing, from pre-registered runs — do not widen):

  * VALID USE — healthy admission calibration. Standardizing a new
    unit's clean log-likelihood by its own commissioning median and
    IQR, mapped onto the shared reference scale, restored the DESIGNED
    false-alarm rate on unseen healthy bearings (0.10% vs 0.5%
    designed, from ~64 s of healthy operation;
    doc/preregistrations/experiment_plan_paderborn3.md §7) at zero severity cost.

  * INVALID USE — the failure alarm. On run-to-failure data the same
    fleet-commissioned margin delayed sustained fault onset by 11–14%
    of unit life, or missed it entirely (doc/preregistrations/experiment_plan_ims.md §4,
    H3L KILLED 3/3): a unit with large healthy IQR divides its damage
    displacement down with it. Failure alarms belong to the unit's own
    accumulated normal history (per-asset construction), not to
    commissioning-standardized fleet margins.

In the three-layer deployment shape (doc/preregistrations/nsad_deployment_principles.md)
this module is layer 2 only: the fleet-prior → asset-posterior bridge.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

__all__ = ['UnitCommissioning', 'commission_unit']


@dataclass(frozen=True)
class UnitCommissioning:
    """Two scalars per unit + the shared reference frame."""
    loc: float        # median of the unit's commissioning log-likelihood
    scale: float      # IQR of the unit's commissioning log-likelihood
    ref_loc: float    # median of the reference clean log-likelihood
    ref_iqr: float    # IQR of the reference clean log-likelihood

    def standardize(self, ll: np.ndarray) -> np.ndarray:
        """Map the unit's log-likelihood onto the reference scale."""
        ll = np.asarray(ll, dtype=np.float64)
        return (ll - self.loc) / self.scale * self.ref_iqr + self.ref_loc

    def alarm_margin(self, ll: np.ndarray, floor: float) -> np.ndarray:
        """Commissioned HEALTHY-ADMISSION margin vs the shared floor.

        Positive = outside the commissioned healthy envelope. See the
        module docstring: this margin controls healthy false alarms;
        it must NOT be the failure alarm (H3L, pre-registration #4).
        """
        return (floor - self.standardize(ll)) / self.ref_iqr


def commission_unit(reference_ll: np.ndarray,
                    commissioning_ll: np.ndarray) -> UnitCommissioning:
    """Estimate a unit's (location, scale) from its healthy
    commissioning log-likelihood under the SHARED geometry.

    Args:
        reference_ll: clean log-likelihood of the shared reference
            (e.g. the floor-calibration part of the fleet model).
        commissioning_ll: the new unit's log-likelihood over its own
            healthy commissioning window, scored under the same shared
            geometry. Healthy data only — never damage periods.
    """
    ref = np.asarray(reference_ll, dtype=np.float64)
    com = np.asarray(commissioning_ll, dtype=np.float64)
    iqr = lambda a: abs(float(np.subtract(*np.percentile(a, [75, 25]))))
    return UnitCommissioning(
        loc=float(np.median(com)), scale=iqr(com) + 1e-12,
        ref_loc=float(np.median(ref)), ref_iqr=iqr(ref) + 1e-12,
    )
