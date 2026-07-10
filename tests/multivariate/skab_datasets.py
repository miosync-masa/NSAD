"""SKAB (Skoltech Anomaly Benchmark) データローダ。

実機ウォーターポンプテストリグの 8 センサー時系列 + 異常ラベル。
https://github.com/waico/SKAB を repo 直下に clone しておく (.gitignore 済):

    git clone --depth 1 https://github.com/waico/SKAB.git SKAB

構造:
    data/anomaly-free/anomaly-free.csv  ラベルなし正常運転 (別の運転点!)
    data/valve1/*.csv   16 files  バルブ1系の故障実験 (ラベル付き)
    data/valve2/*.csv   14 files  バルブ2系
    data/other/*.csv    14 files  キャビテーション等その他故障

注意: anomaly-free.csv はテストファイル群と運転点が大きく異なる
(流量 125 vs 32 等)。per-file の正常構造構築が現実的なプロトコル。

NABSample と同じ属性 (name / values / n / window_indices) を持たせ、
tests/nab/benchmark_nab_selfcal.evaluate_flags を SKAB でも再利用できる形。
"""

from __future__ import annotations

import glob
import os
from dataclasses import dataclass, field
from typing import Iterator, List, Tuple

import numpy as np
import pandas as pd

SKAB_ROOT_DEFAULT = os.path.normpath(
    os.path.join(os.path.dirname(__file__), '..', '..', 'SKAB')
)

SENSOR_COLUMNS = [
    'Accelerometer1RMS', 'Accelerometer2RMS', 'Current', 'Pressure',
    'Temperature', 'Thermocouple', 'Voltage', 'Volume Flow RateRMS',
]

GROUPS = ['valve1', 'valve2', 'other']


@dataclass
class SKABSample:
    name: str                                   # "valve1/0.csv"
    values: np.ndarray                          # (n, 8) float64
    anomaly: np.ndarray                         # (n,) 0/1 labels
    changepoint: np.ndarray                     # (n,) 0/1
    window_indices: List[Tuple[int, int]] = field(default_factory=list)

    @property
    def n(self) -> int:
        return len(self.anomaly)


def _runs(mask: np.ndarray) -> List[Tuple[int, int]]:
    """連続 True 区間の (start, end) inclusive リスト。"""
    diff = np.diff(np.concatenate([[0], mask.astype(np.int8), [0]]))
    starts = np.where(diff == 1)[0]
    ends = np.where(diff == -1)[0] - 1
    return list(zip(starts.tolist(), ends.tolist()))


def load_skab_file(path: str, skab_root: str = SKAB_ROOT_DEFAULT) -> SKABSample:
    df = pd.read_csv(path, sep=';')
    values = df[SENSOR_COLUMNS].to_numpy(dtype=np.float64)
    anomaly = df['anomaly'].to_numpy(dtype=np.float64).astype(np.int32)
    changepoint = df['changepoint'].to_numpy(dtype=np.float64).astype(np.int32)
    rel = os.path.relpath(path, os.path.join(skab_root, 'data'))
    return SKABSample(
        name=rel.replace(os.sep, '/'),
        values=values,
        anomaly=anomaly,
        changepoint=changepoint,
        window_indices=_runs(anomaly.astype(bool)),
    )


def load_anomaly_free(skab_root: str = SKAB_ROOT_DEFAULT) -> np.ndarray:
    """(n, 8) の正常運転データ (ラベルなし、別運転点)。"""
    path = os.path.join(skab_root, 'data', 'anomaly-free', 'anomaly-free.csv')
    df = pd.read_csv(path, sep=';')
    return df[SENSOR_COLUMNS].to_numpy(dtype=np.float64)


def iter_group(group: str,
               skab_root: str = SKAB_ROOT_DEFAULT) -> Iterator[SKABSample]:
    """指定グループ (valve1/valve2/other) の全ファイルを番号順に。"""
    paths = glob.glob(os.path.join(skab_root, 'data', group, '*.csv'))
    paths.sort(key=lambda p: int(os.path.splitext(os.path.basename(p))[0]))
    for p in paths:
        yield load_skab_file(p, skab_root)


def iter_all(skab_root: str = SKAB_ROOT_DEFAULT) -> Iterator[SKABSample]:
    for g in GROUPS:
        yield from iter_group(g, skab_root)
