# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""完整测试套件 - ai-deterministic-control v1.0.0"""

import sys
import os
import json
import tempfile
import shutil
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))

# Use absolute imports when run as script
import os, sys
_pkg = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, _pkg)
from src.algorithms import levenshtein_distance, levenshtein_similarity, tfidf_cosine_similarity, composite_score
from src.config_manager import ConfigManager, DeterministicConfig
from src.seed_manager import SeedManager
from src.consistency_checker import ConsistencyChecker, AlertLevel
from src.monitor_engine import MonitorEngine
from src.model_bridge import ModelBridge


# ============================================================
# Algorithm Tests
# ============================================================
class TestAlgorithms(unittest.TestCase):

    def test_levenshtein_same(self):
        self.assertEqual(levenshtein_distance("hello", "hello"), 0)

    def test_levenshtein_kitten_sitting(self):
        self.assertEqual(levenshtein_distance("kitten", "sitting"), 3)

    def test_levenshtein_empty(self):
        self.assertEqual(levenshtein_distance("", "abc"), 3)

    def test_levenshtein_similarity_same(self):
        self.assertEqual(levenshtein_similarity("abc", "abc"), 1.0)

    def test_levenshtein_similarity_different(self):
        self.assertLess(levenshtein_similarity("abc", "xyz"), 0.5)

    def test_levenshtein_similarity_empty_both(self):
        self.assertEqual(levenshtein_similarity("", ""), 1.0)

    def test_levenshtein_similarity_one_empty(self):
        self.assertEqual(levenshtein_similarity("abc", ""), 0.0)

    def test_tfidf_same_text(self):
        score = tfidf_cosine_similarity("hello world", "hello world")
        self.assertAlmostEqual(score, 1.0, places=5)

    def test_tfidf_similar(self):
        score = tfidf_cosine_similarity("python code", "java code")
        self.assertGreater(score, 0.1)

    def test_tfidf_empty(self):
        self.assertEqual(tfidf_cosine_similarity("", "hello"), 0.0)
        self.assertEqual(tfidf_cosine_similarity("hello", ""), 0.0)

    def test_composite_score(self):
        self.assertAlmostEqual(composite_score(1.0, 1.0), 1.0)
        self.assertAlmostEqual(composite_score(0.0, 0.0), 0.0)
        self.assertAlmostEqual(composite_score(0.5, 0.5), 0.5)


# ============================================================
# ConfigManager Tests
# ============================================================
class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        # Copy presets
        src_presets = os.path.join(os.path.dirname(__file__), "..", "presets", "default.json")
        presets_dir = os.path.join(self.tmpdir, "presets")
        os.makedirs(presets_dir, exist_ok=True)
        shutil.copy2(src_presets, os.path.join(presets_dir, "default.json"))
        self.cm = ConfigManager(skill_dir=self.tmpdir, config_dir=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_default_config(self):
        cfg = self.cm.get_config()
        self.assertEqual(cfg.temperature, 0.3)
        self.assertEqual(cfg.top_p, 0.9)

    def test_set_temperature(self):
        r = self.cm.set_temperature(0.1)
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["temperature"], 0.1)
        self.assertEqual(self.cm.get_config().temperature, 0.1)

    def test_set_temperature_clamp_high(self):
        r = self.cm.set_temperature(3.0)
        self.assertEqual(r["temperature"], 2.0)
        self.assertIn("warning", r)

    def test_set_temperature_clamp_low(self):
        r = self.cm.set_temperature(-0.1)
        self.assertEqual(r["temperature"], 0.0)

    def test_set_top_p_clamp(self):
        r = self.cm.set_top_p(1.5)
        self.assertEqual(r["top_p"], 1.0)
        self.assertIn("warning", r)

    def test_set_seed(self):
        r = self.cm.set_seed(42)
        self.assertEqual(r["seed"], 42)

    def test_apply_preset(self):
        r = self.cm.apply_preset("code_generation")
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["preset"], "code_generation")
        self.assertEqual(self.cm.get_config().temperature, 0.1)

    def test_apply_preset_not_found(self):
        r = self.cm.apply_preset("nonexistent")
        self.assertEqual(r["status"], "error")

    def test_list_presets(self):
        presets = self.cm.list_presets()
        self.assertIn("code_generation", presets)
        self.assertIn("conversation", presets)
        self.assertEqual(len(presets), 6)

    def test_preset_values(self):
        self.assertAlmostEqual(self.cm.presets["code_generation"]["temperature"], 0.1)
        self.assertAlmostEqual(self.cm.presets["config_generation"]["temperature"], 0.2)
        self.assertAlmostEqual(self.cm.presets["conversation"]["temperature"], 0.5)
        self.assertAlmostEqual(self.cm.presets["creative_writing"]["temperature"], 0.8)
        self.assertAlmostEqual(self.cm.presets["data_analysis"]["temperature"], 0.15)
        self.assertAlmostEqual(self.cm.presets["translation"]["temperature"], 0.1)

    def test_config_to_dict(self):
        cfg = DeterministicConfig(temperature=0.1, top_p=0.9, seed=42)
        d = cfg.to_dict()
        self.assertEqual(d["temperature"], 0.1)
        self.assertEqual(d["seed"], 42)


# ============================================================
# SeedManager Tests
# ============================================================
class TestSeedManager(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.sm = SeedManager(data_dir=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_generate(self):
        record = self.sm.generate("test_label")
        self.assertIsNotNone(record.seed)
        self.assertEqual(record.label, "test_label")

    def test_get(self):
        record = self.sm.generate("test")
        got = self.sm.get(record.id)
        self.assertEqual(got.seed, record.seed)

    def test_get_not_found(self):
        self.assertIsNone(self.sm.get("nonexistent"))

    def test_lookup_by_label(self):
        record = self.sm.generate("my_label")
        found = self.sm.lookup_by_label("my_label")
        self.assertEqual(found.id, record.id)

    def test_list_seeds(self):
        self.sm.generate("a")
        self.sm.generate("b")
        self.assertLessEqual(len(self.sm.list_seeds()), 20)

    def test_associate_prompt(self):
        record = self.sm.generate("test")
        self.sm.associate_prompt(record.id, "hello world")
        got = self.sm.get(record.id)
        self.assertIsNotNone(got.prompt_hash)

    def test_reproduce(self):
        record = self.sm.generate("test")
        self.assertEqual(self.sm.reproduce(record.id), record.seed)
        self.assertIsNone(self.sm.reproduce("nonexistent"))


# ============================================================
# ConsistencyChecker Tests
# ============================================================
class TestConsistencyChecker(unittest.TestCase):

    def test_check_identical_outputs(self):
        def sampler(p, c):
            return "identical output"
        checker = ConsistencyChecker()
        report = checker.check("test", sampler, n_samples=3)
        self.assertAlmostEqual(report.composite_score, 1.0, places=5)
        self.assertIsNone(report.alert)

    def test_check_different_outputs(self):
        def sampler(p, c):
            return "output_{}".format(hash(p) % 100)
        checker = ConsistencyChecker()
        report = checker.check("test", sampler, n_samples=3)
        self.assertGreater(report.composite_score, 0.0)

    def test_alert_levels(self):
        # Score < 0.6 → CRITICAL
        checker = ConsistencyChecker()
        alert = checker._check_threshold(0.3)
        self.assertEqual(alert.level, AlertLevel.CRITICAL)

        # 0.6 <= Score < 0.8 → WARN
        alert = checker._check_threshold(0.7)
        self.assertEqual(alert.level, AlertLevel.WARN)

        # Score >= 0.8 → None (OK)
        alert = checker._check_threshold(0.9)
        self.assertIsNone(alert)

    def test_single_sample(self):
        def sampler(p, c):
            return "only one"
        checker = ConsistencyChecker()
        report = checker.check("test", sampler, n_samples=1)
        self.assertEqual(report.alert.level, AlertLevel.CRITICAL)

    def test_default_sampler_returns_something(self):
        result = ConsistencyChecker.default_sampler("hello", {"temperature": 0.3})
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)


# ============================================================
# MonitorEngine Tests
# ============================================================
class TestMonitorEngine(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.monitor = MonitorEngine(data_dir=self.tmpdir)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_record_and_trend(self):
        from src.consistency_checker import ConsistencyReport
        report = ConsistencyReport(
            samples=["a", "a", "a"], char_similarity=1.0,
            semantic_similarity=1.0, composite_score=0.95,
        )
        config = DeterministicConfig()
        self.monitor.record_check(report, config)
        trend = self.monitor.analyze_trend()
        self.assertEqual(trend.data_points, 1)

    def test_no_data(self):
        trend = self.monitor.analyze_trend()
        self.assertEqual(trend.status, "no_data")

    def test_anomalies_insufficient(self):
        anomalies = self.monitor.detect_anomalies()
        self.assertEqual(anomalies, [])

    def test_generate_report(self):
        report = self.monitor.generate_report(fmt="markdown")
        self.assertIn("Monitor Report", report)

    def test_generate_report_json(self):
        report = self.monitor.generate_report(fmt="json")
        data = json.loads(report)
        self.assertIn("trend", data)

    def test_zscore_detection(self):
        from src.consistency_checker import ConsistencyReport
        # Add normal scores
        for i in range(5):
            self.monitor.record_check(
                ConsistencyReport(samples=["a"] * 3, char_similarity=0.9,
                                  semantic_similarity=0.9, composite_score=0.9),
                DeterministicConfig()
            )
        # Add anomaly
        self.monitor.record_check(
            ConsistencyReport(samples=["a"] * 3, char_similarity=0.1,
                              semantic_similarity=0.1, composite_score=0.1),
            DeterministicConfig()
        )
        anomalies = self.monitor.detect_anomalies()
        self.assertGreater(len(anomalies), 0)


# ============================================================
# ModelBridge Tests
# ============================================================
class TestModelBridge(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.config_path = os.path.join(self.tmpdir, "openclaw.json")
        # Write test config
        test_config = {
            "models": {
                "glm-5": {"parameters": {"temperature": 0.7}},
                "deepseek": {"parameters": {}}
            }
        }
        with open(self.config_path, "w") as f:
            json.dump(test_config, f)
        self.bridge = ModelBridge(config_path=self.config_path)

    def tearDown(self):
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_read_current(self):
        data = self.bridge.read_current()
        self.assertIn("glm-5", data["models"])

    def test_inject_params(self):
        config = DeterministicConfig(temperature=0.1, top_p=0.85, seed=42)
        result = self.bridge.inject_params(config)
        self.assertEqual(result["models"]["glm-5"]["parameters"]["temperature"], 0.1)
        self.assertEqual(result["models"]["deepseek"]["parameters"]["temperature"], 0.1)
        self.assertEqual(result["models"]["glm-5"]["parameters"]["seed"], 42)

    def test_inject_single_model(self):
        config = DeterministicConfig(temperature=0.2)
        self.bridge.inject_model_params("glm-5", config)
        data = self.bridge.read_current()
        self.assertEqual(data["models"]["glm-5"]["parameters"]["temperature"], 0.2)

    def test_reset_params(self):
        config = DeterministicConfig(temperature=0.01, top_p=0.5)
        self.bridge.inject_params(config)
        self.bridge.reset_params()
        data = self.bridge.read_current()
        self.assertEqual(data["models"]["glm-5"]["parameters"]["temperature"], 0.3)

    def test_backup_and_restore(self):
        config = DeterministicConfig(temperature=0.1)
        self.bridge.inject_params(config)
        # Verify backup exists
        self.assertTrue(os.path.exists(self.config_path + ".bak"))

    def test_missing_config(self):
        bridge = ModelBridge(config_path="/nonexistent/path.json")
        data = bridge.read_current()
        self.assertEqual(data, {"models": {}})


# ============================================================
# Integration Test
# ============================================================
class TestIntegration(unittest.TestCase):

    def test_full_workflow(self):
        tmpdir = tempfile.mkdtemp()
        try:
            # Copy presets
            src_presets = os.path.join(os.path.dirname(__file__), "..", "presets", "default.json")
            presets_dir = os.path.join(tmpdir, "presets")
            os.makedirs(presets_dir, exist_ok=True)
            shutil.copy2(src_presets, os.path.join(presets_dir, "default.json"))

            cm = ConfigManager(skill_dir=tmpdir, config_dir=tmpdir)
            result = cm.apply_preset("code_generation")
            self.assertEqual(result["status"], "ok")
            self.assertEqual(cm.get_config().temperature, 0.1)

            checker = ConsistencyChecker(cm.get_config())
            def sampler(p, c):
                return "deterministic output"
            report = checker.check("write a sort function", sampler, n_samples=3)
            self.assertAlmostEqual(report.composite_score, 1.0, places=5)

            monitor = MonitorEngine(data_dir=os.path.join(tmpdir, "data"))
            monitor.record_check(report, cm.get_config())
            trend = monitor.analyze_trend()
            self.assertEqual(trend.data_points, 1)
        finally:
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
