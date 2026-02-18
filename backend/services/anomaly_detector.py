import math
from dataclasses import dataclass, field


@dataclass
class AnomalyResult:
    key: str
    value: float
    mean: float
    stddev: float
    z_score: float
    is_anomaly: bool
    severity: str  # "none" | "low" | "medium" | "critical"


@dataclass
class _StreamState:
    count: int = 0
    mean: float = 0.0
    m2: float = 0.0

    @property
    def variance(self) -> float:
        if self.count < 2:
            return 0.0
        return self.m2 / self.count

    @property
    def stddev(self) -> float:
        return math.sqrt(self.variance)


class WelfordDetector:
    def __init__(self, min_samples: int = 10):
        self.min_samples = min_samples
        self._streams: dict[str, _StreamState] = {}

    def update(self, key: str, value: float) -> AnomalyResult:
        state = self._streams.get(key)
        if state is None:
            state = _StreamState()
            self._streams[key] = state

        # Welford online update
        state.count += 1
        delta = value - state.mean
        state.mean += delta / state.count
        delta2 = value - state.mean
        state.m2 += delta * delta2

        # Determine anomaly status
        if state.count < self.min_samples or state.stddev == 0.0:
            return AnomalyResult(
                key=key,
                value=value,
                mean=state.mean,
                stddev=state.stddev,
                z_score=0.0,
                is_anomaly=False,
                severity="none",
            )

        z_score = abs(value - state.mean) / state.stddev

        if z_score >= 3.0:
            severity = "critical"
        elif z_score >= 2.0:
            severity = "medium"
        elif z_score >= 1.5:
            severity = "low"
        else:
            severity = "none"

        is_anomaly = z_score >= 1.5

        return AnomalyResult(
            key=key,
            value=value,
            mean=state.mean,
            stddev=state.stddev,
            z_score=z_score,
            is_anomaly=is_anomaly,
            severity=severity,
        )
