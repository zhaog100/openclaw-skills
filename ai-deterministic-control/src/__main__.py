# Copyright (c) 2026 思捷娅科技 (SJYKJ)

"""
CLI 参数解析入口
"""

import sys
import os
import argparse
import json

# Add src dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config_manager import ConfigManager
from consistency_checker import ConsistencyChecker
from seed_manager import SeedManager
from monitor_engine import MonitorEngine
from model_bridge import ModelBridge


def cmd_set(args):
    cm = ConfigManager()
    result = {}
    if args.temperature is not None:
        result.update(cm.set_temperature(args.temperature))
    if args.top_p is not None:
        result.update(cm.set_top_p(args.top_p))
    if args.seed is not None:
        result.update(cm.set_seed(args.seed))
    if not result:
        cfg = cm.get_config()
        result = {"status": "ok", "current": cfg.to_dict()}
    print(json.dumps(result, ensure_ascii=False, indent=2))


def cmd_check(args):
    cm = ConfigManager()
    checker = ConsistencyChecker(cm.get_config())
    prompt = args.prompt or "Hello, how are you?"

    def mock_sampler(prompt_text, config):
        return "[mock] deterministic output for: " + prompt_text[:20]

    report = checker.check(prompt, mock_sampler, n_samples=args.samples)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))

    # Record to monitor
    try:
        monitor = MonitorEngine()
        monitor.record_check(report, cm.get_config())
    except Exception:
        pass


def cmd_report(args):
    monitor = MonitorEngine()
    print(monitor.generate_report(fmt=args.format, days=args.days))


def cmd_preset(args):
    cm = ConfigManager()
    if args.action == "list":
        print(json.dumps(cm.list_presets(), ensure_ascii=False, indent=2))
    elif args.action == "apply":
        result = cm.apply_preset(args.name)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        # Signal file
        if result.get("status") == "ok":
            _write_signal(cm)
    elif args.action == "create":
        print(json.dumps({"status": "error", "message": "custom preset creation not supported yet"}, ensure_ascii=False))
    else:
        print(json.dumps({"status": "error", "message": "use: list | apply <name>"}))


def cmd_monitor(args):
    monitor = MonitorEngine()
    if args.action == "status":
        trend = monitor.analyze_trend()
        print(json.dumps(trend.to_dict(), ensure_ascii=False, indent=2))
    elif args.action == "trend":
        trend = monitor.analyze_trend(args.days)
        print(json.dumps(trend.to_dict(), ensure_ascii=False, indent=2))
    elif args.action == "anomalies":
        anomalies = [a.to_dict() for a in monitor.detect_anomalies()]
        print(json.dumps({"anomalies": anomalies, "count": len(anomalies)}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"status": "error", "message": "use: status | trend | anomalies"}))


def cmd_inject(args):
    cm = ConfigManager()
    bridge = ModelBridge(args.config_path)
    config = cm.get_config()
    if args.model:
        result = bridge.inject_model_params(args.model, config)
    else:
        result = bridge.inject_params(config, dry_run=args.dry_run)
    print(json.dumps({"status": "ok", "injected": config.to_dict()}, ensure_ascii=False, indent=2))


def cmd_reset(args):
    bridge = ModelBridge(args.config_path)
    targets = None
    if args.all_targets:
        targets = None
    else:
        t = []
        if args.temperature:
            t.append("temperature")
        if args.seed:
            t.append("seed")
        if t:
            targets = t
        else:
            targets = None
    try:
        result = bridge.reset_params(targets)
        print(json.dumps({"status": "ok", "message": "params reset"}, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))


def _write_signal(cm):
    """写信号文件"""
    signal_path = os.path.expanduser("~/.openclaw/workspace/.detcontrol_signal.json")
    cfg = cm.get_config()
    signal = {
        "mode": "deterministic",
        "recommended_temperature": cfg.temperature,
        "reason": cfg.active_preset or "manual_set",
        "preset_name": cfg.active_preset,
        "timestamp": cm.config.get("last_modified", ""),
    }
    try:
        with open(signal_path, "w") as f:
            json.dump(signal, f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def main():
    parser = argparse.ArgumentParser(prog="detcontrol", description="AI 确定性控制工具")
    sub = parser.add_subparsers(dest="command")

    # set
    p_set = sub.add_parser("set")
    p_set.add_argument("--temperature", "--temp", type=float)
    p_set.add_argument("--top-p", "--top_p", type=float)
    p_set.add_argument("--seed", type=int)

    # check
    p_check = sub.add_parser("check")
    p_check.add_argument("--prompt", type=str)
    p_check.add_argument("--samples", type=int, default=5)
    p_check.add_argument("--threshold", type=float, default=0.8)

    # report
    p_report = sub.add_parser("report")
    p_report.add_argument("--format", choices=["markdown", "json"], default="markdown")
    p_report.add_argument("--days", type=int, default=7)

    # preset
    p_preset = sub.add_parser("preset")
    p_preset.add_argument("action", choices=["list", "apply", "create"])
    p_preset.add_argument("name", nargs="?")

    # monitor
    p_monitor = sub.add_parser("monitor")
    p_monitor.add_argument("action", choices=["status", "trend", "anomalies"])
    p_monitor.add_argument("--days", type=int, default=7)

    # inject
    p_inject = sub.add_parser("inject")
    p_inject.add_argument("--model", type=str)
    p_inject.add_argument("--config-path", type=str)
    p_inject.add_argument("--dry-run", action="store_true")

    # reset
    p_reset = sub.add_parser("reset")
    p_reset.add_argument("--all", dest="all_targets", action="store_true")
    p_reset.add_argument("--temperature", action="store_true")
    p_reset.add_argument("--seed", action="store_true")
    p_reset.add_argument("--config-path", type=str)

    args = parser.parse_args()
    if args.command == "set":
        cmd_set(args)
    elif args.command == "check":
        cmd_check(args)
    elif args.command == "report":
        cmd_report(args)
    elif args.command == "preset":
        cmd_preset(args)
    elif args.command == "monitor":
        cmd_monitor(args)
    elif args.command == "inject":
        cmd_inject(args)
    elif args.command == "reset":
        cmd_reset(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
