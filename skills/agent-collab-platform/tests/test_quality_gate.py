#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""
test_quality_gate.py - 质量保障插件单元测试
"""

import json
import os
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# 确保导入路径
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agents.agent_a.quality_gate import (
    PipelineConfig,
    read_prd,
    plan_review,
    review,
    fix,
    publish,
    check_status,
    run_quality_gate,
    _source_and_call,
    _run_pipeline_cmd,
)


# ─── Fixtures ───

@pytest.fixture
def mock_config(tmp_path):
    """创建临时配置文件"""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "pipeline_config.json"
    config_file.write_text(json.dumps({
        "review_pass_score": 50,
        "max_fix_rounds": 3,
        "auto_publish": True,
        "pipeline_path": str(tmp_path / "auto-pipeline"),
    }))
    return PipelineConfig(str(config_file))


@pytest.fixture
def mock_skill_dir(tmp_path):
    """创建模拟技能目录"""
    skill_dir = tmp_path / "mock_skill"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text("# Mock Skill")
    return str(skill_dir)


@pytest.fixture
def sample_prd(tmp_path):
    """创建示例 PRD 文件"""
    prd_path = tmp_path / "test_PRD.md"
    prd_path.write_text("# Test Skill PRD\n\n## 需求\n- 功能A\n- 功能B\n")
    return str(prd_path)


@pytest.fixture
def sample_approved_tasks():
    return {
        "title": "test_skill",
        "tasks": [{"id": 1, "title": "功能A", "priority": "high"}],
    }


@pytest.fixture
def sample_review_result():
    return {
        "total_score": 45,
        "max_score": 100,
        "passed": False,
        "dimensions": [{"name": "测试覆盖", "score": 3, "weight": 2, "details": "ok"}],
        "issues": [
            {"severity": "major", "dimension": "测试覆盖", "desc": "缺少测试"}
        ],
    }


# ─── 配置测试 ───

class TestPipelineConfig:
    def test_load_config(self, mock_config):
        assert mock_config.review_pass_score == 50
        assert mock_config.max_fix_rounds == 3
        assert mock_config.auto_publish is True

    def test_pipeline_path_resolution(self, mock_config, tmp_path):
        expected = str(tmp_path / "auto-pipeline")
        assert mock_config.pipeline_path == expected

    def test_pipeline_sh(self, mock_config, tmp_path):
        assert mock_config.pipeline_sh == str(tmp_path / "auto-pipeline" / "pipeline.sh")

    def test_missing_config_file(self):
        with pytest.raises(FileNotFoundError):
            PipelineConfig("/nonexistent/path/pipeline_config.json")


# ─── 接口调用测试 ───

class TestReadPrd:
    @patch("agents.agent_a.quality_gate._source_and_call")
    def test_read_prd_success(self, mock_call, mock_config, sample_prd):
        mock_call.return_value = (0, json.dumps({"tasks": [{"id": 1}]}), "")
        result = read_prd(sample_prd, mock_config)
        assert "tasks" in result
        mock_call.assert_called_once()

    @patch("agents.agent_a.quality_gate._source_and_call")
    def test_read_prd_calls_correct_function(self, mock_call, mock_config, sample_prd):
        mock_call.return_value = (0, json.dumps({"tasks": []}), "")
        read_prd(sample_prd, mock_config)
        args = mock_call.call_args[0]
        assert args[1] == "prd_read"
        assert sample_prd in args[2]


class TestPlanReview:
    @patch("agents.agent_a.quality_gate._source_and_call")
    def test_plan_review_with_dict(self, mock_call, mock_config, sample_approved_tasks):
        mock_call.return_value = (0, json.dumps(sample_approved_tasks), "")
        result = plan_review(sample_approved_tasks, mock_config)
        assert result["title"] == "test_skill"

    @patch("agents.agent_a.quality_gate._source_and_call")
    def test_plan_review_with_json_string(self, mock_call, mock_config):
        tasks_json = json.dumps({"title": "test", "tasks": []})
        mock_call.return_value = (0, tasks_json, "")
        result = plan_review(tasks_json, mock_config)
        assert result["title"] == "test"


class TestReview:
    @patch("agents.agent_a.quality_gate._source_and_call")
    def test_review_returns_score(self, mock_call, mock_config, mock_skill_dir, sample_approved_tasks):
        review_json = json.dumps({
            "total_score": 60, "max_score": 100, "passed": True,
            "dimensions": [], "issues": [],
        })
        mock_call.return_value = (0, review_json, "")
        result = review(mock_skill_dir, sample_approved_tasks, mock_config)
        assert result["total_score"] == 60
        assert result["passed"] is True


class TestFix:
    @patch("agents.agent_a.quality_gate._source_and_call")
    def test_fix_returns_prompt(self, mock_call, mock_config, mock_skill_dir, sample_review_result):
        mock_call.return_value = (0, "修复提示: 请添加测试用例", "")
        issues = sample_review_result["issues"]
        result = fix(mock_skill_dir, issues, sample_review_result, mock_config)
        assert "修复提示" in result


class TestPublish:
    @patch("agents.agent_a.quality_gate._source_and_call")
    def test_publish_success(self, mock_call, mock_config, mock_skill_dir, sample_review_result):
        mock_call.return_value = (0, json.dumps({"status": "published"}), "")
        result = publish(mock_skill_dir, sample_review_result, mock_config)
        assert result["status"] == "published"


class TestCheckStatus:
    @patch("agents.agent_a.quality_gate._source_and_call")
    def test_check_status(self, mock_call, mock_config):
        mock_call.return_value = (0, json.dumps({"status": "reviewing"}), "")
        result = check_status("test_skill", mock_config)
        assert result["status"] == "reviewing"


class TestRunQualityGate:
    @patch("agents.agent_a.quality_gate.publish")
    @patch("agents.agent_a.quality_gate.fix")
    @patch("agents.agent_a.quality_gate.review")
    @patch("agents.agent_a.quality_gate.plan_review")
    @patch("agents.agent_a.quality_gate.read_prd")
    def test_gate_pass_on_first_review(
        self, mock_read, mock_plan, mock_review, mock_fix, mock_publish,
        mock_config, mock_skill_dir, sample_prd,
    ):
        mock_read.return_value = {"tasks": [{"id": 1}]}
        mock_plan.return_value = {"tasks": [{"id": 1}], "title": "test"}
        mock_review.return_value = {
            "total_score": 70, "max_score": 100, "passed": True,
            "dimensions": [], "issues": [],
        }
        result = run_quality_gate(mock_skill_dir, sample_prd, mock_config)
        assert result["passed"] is True
        assert result["fix_rounds"] == 0
        assert result["published"] is True
        mock_fix.assert_not_called()

    @patch("agents.agent_a.quality_gate.publish")
    @patch("agents.agent_a.quality_gate.fix")
    @patch("agents.agent_a.quality_gate.review")
    @patch("agents.agent_a.quality_gate.plan_review")
    @patch("agents.agent_a.quality_gate.read_prd")
    def test_gate_fix_then_pass(
        self, mock_read, mock_plan, mock_review, mock_fix, mock_publish,
        mock_config, mock_skill_dir, sample_prd, sample_review_result,
    ):
        mock_read.return_value = {"tasks": [{"id": 1}]}
        mock_plan.return_value = {"tasks": [{"id": 1}], "title": "test"}
        # 第一次 review 不通过，第二次通过
        mock_review.side_effect = [
            sample_review_result,
            {
                "total_score": 65, "max_score": 100, "passed": True,
                "dimensions": [], "issues": [],
            },
        ]
        result = run_quality_gate(mock_skill_dir, sample_prd, mock_config)
        assert result["passed"] is True
        assert result["fix_rounds"] == 1
        assert mock_fix.call_count == 1

    @patch("agents.agent_a.quality_gate.publish")
    @patch("agents.agent_a.quality_gate.fix")
    @patch("agents.agent_a.quality_gate.review")
    def test_gate_without_prd(
        self, mock_review, mock_fix, mock_publish,
        mock_config, mock_skill_dir,
    ):
        mock_review.return_value = {
            "total_score": 55, "max_score": 100, "passed": True,
            "dimensions": [], "issues": [],
        }
        result = run_quality_gate(mock_skill_dir, config=mock_config)
        assert result["passed"] is True
        assert result["fix_rounds"] == 0

    @patch("agents.agent_a.quality_gate.publish", side_effect=Exception("发布失败"))
    @patch("agents.agent_a.quality_gate.review")
    def test_gate_publish_error_handled(
        self, mock_review, mock_publish,
        mock_config, mock_skill_dir,
    ):
        mock_review.return_value = {
            "total_score": 80, "max_score": 100, "passed": True,
            "dimensions": [], "issues": [],
        }
        result = run_quality_gate(mock_skill_dir, config=mock_config)
        assert result["passed"] is True
        assert result["published"] is False
        assert "publish_error" in result
