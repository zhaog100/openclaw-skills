#!/usr/bin/env python3
"""异常检测告警模块"""

import json
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, List, Optional


class AlertManager:
    """异常检测告警管理器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "alert_config.json"
        self.config = self._load_config()
        self.alerts_file = Path(__file__).parent / "alerts_history.json"
        self.alerts_history = self._load_alerts()
    
    def _load_config(self) -> Dict:
        """加载告警配置"""
        if not self.config_path.exists():
            # 默认配置
            default_config = {
                "thresholds": {
                    "similarity_warning": 60.0,
                    "similarity_critical": 40.0,
                    "error_rate_warning": 0.1,
                    "error_rate_critical": 0.3
                },
                "channels": {
                    "email": {
                        "enabled": False,
                        "smtp_server": "smtp.gmail.com",
                        "smtp_port": 587,
                        "sender": "",
                        "password": "",
                        "recipients": []
                    },
                    "feishu": {
                        "enabled": False,
                        "webhook_url": ""
                    },
                    "dingtalk": {
                        "enabled": False,
                        "webhook_url": ""
                    }
                },
                "rules": {
                    "cooldown_minutes": 10,
                    "max_alerts_per_hour": 10,
                    "aggregation_enabled": True
                }
            }
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(default_config, f, indent=2, ensure_ascii=False)
            
            return default_config
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_alerts(self) -> List[Dict]:
        """加载告警历史"""
        if not self.alerts_file.exists():
            return []
        
        with open(self.alerts_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("alerts", [])
    
    def _save_alerts(self):
        """保存告警历史"""
        data = {"alerts": self.alerts_history[-100:]}  # 保留最近100条
        
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def detect_anomaly(self, similarity: float, prompt: str, output: str) -> Optional[Dict]:
        """检测异常
        
        Args:
            similarity: 相似度
            prompt: 提示词
            output: 输出内容
        
        Returns:
            异常信息（无异常则返回None）
        """
        thresholds = self.config["thresholds"]
        
        if similarity < thresholds["similarity_critical"]:
            return {
                "level": "critical",
                "type": "low_similarity",
                "message": f"相似度过低: {similarity}% (阈值: {thresholds['similarity_critical']}%)",
                "similarity": similarity,
                "threshold": thresholds["similarity_critical"],
                "prompt": prompt[:100],
                "timestamp": datetime.now().isoformat()
            }
        
        elif similarity < thresholds["similarity_warning"]:
            return {
                "level": "warning",
                "type": "low_similarity",
                "message": f"相似度较低: {similarity}% (阈值: {thresholds['similarity_warning']}%)",
                "similarity": similarity,
                "threshold": thresholds["similarity_warning"],
                "prompt": prompt[:100],
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    def should_send_alert(self, anomaly: Dict) -> bool:
        """判断是否应该发送告警（冷却和聚合逻辑）
        
        Args:
            anomaly: 异常信息
        
        Returns:
            是否发送告警
        """
        rules = self.config["rules"]
        
        # 检查冷却时间
        cooldown_minutes = rules["cooldown_minutes"]
        recent_alerts = [
            a for a in self.alerts_history
            if self._is_recent_alert(a, cooldown_minutes)
        ]
        
        # 检查每小时最大告警数
        if len(recent_alerts) >= rules["max_alerts_per_hour"]:
            return False
        
        # 如果启用聚合，检查是否有相同类型的最近告警
        if rules["aggregation_enabled"]:
            for alert in recent_alerts:
                if (alert.get("type") == anomaly["type"] and
                    alert.get("level") == anomaly["level"]):
                    return False
        
        return True
    
    def _is_recent_alert(self, alert: Dict, minutes: int) -> bool:
        """检查告警是否在指定分钟内"""
        alert_time = datetime.fromisoformat(alert["timestamp"])
        now = datetime.now()
        delta = now - alert_time
        return delta.total_seconds() < minutes * 60
    
    def send_alert(self, anomaly: Dict) -> Dict:
        """发送告警
        
        Args:
            anomaly: 异常信息
        
        Returns:
            发送结果
        """
        # 记录告警
        self.alerts_history.append(anomaly)
        self._save_alerts()
        
        # 检查是否应该发送
        if not self.should_send_alert(anomaly):
            return {
                "sent": False,
                "reason": "告警被抑制（冷却或聚合）",
                "anomaly": anomaly
            }
        
        results = {}
        channels = self.config["channels"]
        
        # 发送邮件
        if channels["email"]["enabled"]:
            results["email"] = self._send_email(anomaly)
        
        # 发送飞书
        if channels["feishu"]["enabled"]:
            results["feishu"] = self._send_feishu(anomaly)
        
        # 发送钉钉
        if channels["dingtalk"]["enabled"]:
            results["dingtalk"] = self._send_dingtalk(anomaly)
        
        return {
            "sent": True,
            "channels": results,
            "anomaly": anomaly
        }
    
    def _send_email(self, anomaly: Dict) -> Dict:
        """发送邮件告警"""
        try:
            email_config = self.config["channels"]["email"]
            
            msg = MIMEMultipart()
            msg['From'] = email_config["sender"]
            msg['To'] = ", ".join(email_config["recipients"])
            msg['Subject'] = f"[{anomaly['level'].upper()}] AI确定性控制异常告警"
            
            body = f"""
异常检测告警

级别: {anomaly['level']}
类型: {anomaly['type']}
消息: {anomaly['message']}
时间: {anomaly['timestamp']}

提示词: {anomaly['prompt']}
相似度: {anomaly['similarity']}%
阈值: {anomaly['threshold']}%

---
AI确定性控制工具
            """
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件（模拟，实际需要配置SMTP）
            # with smtplib.SMTP(email_config["smtp_server"], email_config["smtp_port"]) as server:
            #     server.starttls()
            #     server.login(email_config["sender"], email_config["password"])
            #     server.send_message(msg)
            
            return {
                "success": True,
                "message": "邮件告警已发送（模拟）"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_feishu(self, anomaly: Dict) -> Dict:
        """发送飞书告警"""
        try:
            import requests
            
            webhook_url = self.config["channels"]["feishu"]["webhook_url"]
            
            if not webhook_url:
                return {
                    "success": False,
                    "error": "飞书Webhook URL未配置"
                }
            
            # 构造飞书消息
            payload = {
                "msg_type": "text",
                "content": {
                    "text": f"[{anomaly['level'].upper()}] {anomaly['message']}\n时间: {anomaly['timestamp']}"
                }
            }
            
            # 发送请求（模拟）
            # response = requests.post(webhook_url, json=payload)
            
            return {
                "success": True,
                "message": "飞书告警已发送（模拟）"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _send_dingtalk(self, anomaly: Dict) -> Dict:
        """发送钉钉告警"""
        try:
            import requests
            
            webhook_url = self.config["channels"]["dingtalk"]["webhook_url"]
            
            if not webhook_url:
                return {
                    "success": False,
                    "error": "钉钉Webhook URL未配置"
                }
            
            # 构造钉钉消息
            payload = {
                "msgtype": "text",
                "text": {
                    "content": f"[{anomaly['level'].upper()}] {anomaly['message']}\n时间: {anomaly['timestamp']}"
                }
            }
            
            # 发送请求（模拟）
            # response = requests.post(webhook_url, json=payload)
            
            return {
                "success": True,
                "message": "钉钉告警已发送（模拟）"
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_alert_stats(self) -> Dict:
        """获取告警统计"""
        if not self.alerts_history:
            return {
                "total_alerts": 0,
                "message": "暂无告警记录"
            }
        
        # 统计各级别告警
        level_counts = {}
        type_counts = {}
        
        for alert in self.alerts_history:
            level = alert.get("level", "unknown")
            level_counts[level] = level_counts.get(level, 0) + 1
            
            alert_type = alert.get("type", "unknown")
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        # 最近24小时告警
        recent_24h = [
            a for a in self.alerts_history
            if self._is_recent_alert(a, 24 * 60)
        ]
        
        return {
            "total_alerts": len(self.alerts_history),
            "level_distribution": level_counts,
            "type_distribution": type_counts,
            "recent_24h": len(recent_24h),
            "latest_alert": self.alerts_history[-1] if self.alerts_history else None
        }
    
    def configure_channel(self, channel: str, config: Dict):
        """配置告警渠道
        
        Args:
            channel: 渠道名称（email/feishu/dingtalk）
            config: 配置信息
        """
        if channel in self.config["channels"]:
            self.config["channels"][channel].update(config)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)


# ========== CLI命令 ==========

def alert_command(similarity: float, prompt: str, output: str = ""):
    """异常检测告警命令"""
    manager = AlertManager()
    
    # 检测异常
    anomaly = manager.detect_anomaly(similarity, prompt, output)
    
    if anomaly is None:
        print(f"\n✅ 未检测到异常（相似度: {similarity}%）\n")
        return {"detected": False}
    
    # 发送告警
    result = manager.send_alert(anomaly)
    
    print(f"\n⚠️  检测到异常！\n")
    print(f"级别: {anomaly['level']}")
    print(f"类型: {anomaly['type']}")
    print(f"消息: {anomaly['message']}")
    print(f"时间: {anomaly['timestamp']}\n")
    
    if result["sent"]:
        print("告警已发送:")
        for channel, status in result["channels"].items():
            status_icon = "✅" if status.get("success") else "❌"
            print(f"  {status_icon} {channel}: {status.get('message', status.get('error'))}")
    else:
        print(f"告警未发送: {result['reason']}")
    
    print()
    
    return result
