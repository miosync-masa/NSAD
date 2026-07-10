"""Structural input adapters (architecture.md §13.1).

Validated, fault-agnostic vocabularies promoted from the experiment
path (§13.8 promotion log: §13.9). The qualification law (§13.2)
binds every adapter here: causal, self-calibrated, no anomaly-shape
knowledge, severity-preserving.
"""

from ..features.extractor import extract_cycle_phase_features
from .vibration import (envelope_bands, spectral_entropy,
                        vibration_bands, vibration_features)

__all__ = ['vibration_features', 'vibration_bands', 'envelope_bands',
           'spectral_entropy', 'extract_cycle_phase_features']
