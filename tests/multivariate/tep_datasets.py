"""TEP (Tennessee Eastman Process) データローダ — Braatz 標準配布版。

https://github.com/camaramm/tennessee-eastman-profBraatz を repo 直下に
clone しておく (.gitignore 済):

    git clone --depth 1 https://github.com/camaramm/tennessee-eastman-profBraatz.git TEP

構造 (community-standard, 3-min sampling, 52 process variables):
    d00.dat      fault-free training, 500 samples — **分離されたクリーン正常ログ**
                 (格納が転置 (52, 500) なので .T する)
    d00_te.dat   fault-free test, 960 samples (FAR 測定用)
    dXX.dat      fault XX training (未使用 — 異常形状は学習しない)
    dXX_te.dat   fault XX test, 960 samples, fault は sample 160 から active

NAB/SKAB と違い、TEP は「正常運転ログが独立に与えられる」理想的産業設定:
正常構造の構築に除外マスクすら不要 (legitimacy rule の ideal 側)。
TEP はシミュレーションである (20 年来の公開標準ベンチ) — 論文では
SKAB (実機) とペアで開示する。
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Iterator

import numpy as np

TEP_ROOT_DEFAULT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'TEP')
)

FAULT_START = 160          # fault active from this sample in *_te files
N_FAULTS = 21


@dataclass
class TEPSample:
    name: str              # "d01_te"
    fault_id: int          # 1..21 (0 = fault-free test)
    values: np.ndarray     # (960, 52)

    @property
    def n(self) -> int:
        return len(self.values)

    @property
    def fault_mask(self) -> np.ndarray:
        m = np.zeros(self.n, dtype=bool)
        if self.fault_id > 0:
            m[FAULT_START:] = True
        return m


def load_train_normal(tep_root: str = TEP_ROOT_DEFAULT) -> np.ndarray:
    """d00 fault-free training data, (500, 52)。転置格納を補正。"""
    X = np.loadtxt(os.path.join(tep_root, 'd00.dat'))
    if X.shape[0] == 52:       # stored transposed
        X = X.T
    return np.asarray(X, dtype=np.float64)


def load_test(fault_id: int, tep_root: str = TEP_ROOT_DEFAULT) -> TEPSample:
    name = f"d{fault_id:02d}_te"
    X = np.loadtxt(os.path.join(tep_root, f"{name}.dat"))
    return TEPSample(name=name, fault_id=fault_id,
                     values=np.asarray(X, dtype=np.float64))


def iter_faults(tep_root: str = TEP_ROOT_DEFAULT) -> Iterator[TEPSample]:
    for f in range(1, N_FAULTS + 1):
        yield load_test(f, tep_root)
