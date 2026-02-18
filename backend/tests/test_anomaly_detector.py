import pytest
from services.anomaly_detector import WelfordDetector, AnomalyResult


class TestNoAnomalyWithStableData:
    def test_100_identical_values_not_anomaly(self):
        detector = WelfordDetector(min_samples=10)
        for _ in range(100):
            result = detector.update("metric", 42.0)
        assert result.is_anomaly is False
        assert result.severity == "none"
        assert result.z_score == 0.0


class TestDetectsSpike:
    def test_spike_after_stable_values(self):
        detector = WelfordDetector(min_samples=10)
        for _ in range(50):
            result = detector.update("metric", 100.0)
        # Inject a value that is 2x the stable value
        result = detector.update("metric", 200.0)
        assert result.is_anomaly is True
        assert result.z_score >= 3.0
        assert result.severity == "critical"


class TestNeedsMinimumSamples:
    def test_first_update_no_anomaly(self):
        detector = WelfordDetector(min_samples=10)
        result = detector.update("metric", 999.0)
        assert result.is_anomaly is False
        assert result.z_score == 0.0
        assert result.severity == "none"

    def test_below_min_samples_no_anomaly(self):
        detector = WelfordDetector(min_samples=10)
        for i in range(9):
            result = detector.update("metric", float(i * 1000))
        assert result.is_anomaly is False
        assert result.z_score == 0.0


class TestSeverityLevels:
    def _build_detector(self, mean: float, stddev: float, count: int = 10000):
        """Helper: build a detector with known statistics using Welford updates.

        Uses a large sample count so one additional value barely shifts stats.
        """
        detector = WelfordDetector(min_samples=10)
        for _ in range(count // 2):
            detector.update("k", mean + stddev)
            detector.update("k", mean - stddev)
        return detector

    def test_below_1_5_is_none(self):
        detector = self._build_detector(mean=100.0, stddev=10.0)
        result = detector.update("k", 100.0 + 10.0 * 1.4)
        assert result.is_anomaly is False
        assert result.severity == "none"

    def test_at_1_5_is_low(self):
        detector = self._build_detector(mean=100.0, stddev=10.0)
        # Use 1.6 to be clearly above 1.5 threshold after stats shift
        result = detector.update("k", 100.0 + 10.0 * 1.6)
        assert result.is_anomaly is True
        assert result.severity == "low"

    def test_at_2_0_is_medium(self):
        detector = self._build_detector(mean=100.0, stddev=10.0)
        # Use 2.1 to be clearly above 2.0 threshold after stats shift
        result = detector.update("k", 100.0 + 10.0 * 2.1)
        assert result.is_anomaly is True
        assert result.severity == "medium"

    def test_at_3_0_is_critical(self):
        detector = self._build_detector(mean=100.0, stddev=10.0)
        # Use 3.1 to be clearly above 3.0 threshold after stats shift
        result = detector.update("k", 100.0 + 10.0 * 3.1)
        assert result.is_anomaly is True
        assert result.severity == "critical"


class TestIndependentStreams:
    def test_spike_in_a_does_not_affect_b(self):
        detector = WelfordDetector(min_samples=10)
        for _ in range(50):
            detector.update("A", 100.0)
            detector.update("B", 100.0)
        # Spike in A
        result_a = detector.update("A", 500.0)
        # Normal value in B
        result_b = detector.update("B", 100.0)
        assert result_a.is_anomaly is True
        assert result_b.is_anomaly is False
        assert result_b.severity == "none"
