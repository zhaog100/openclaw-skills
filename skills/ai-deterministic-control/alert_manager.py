#!/usr/bin/env python3
"""告警管理器模块"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from config import ConfigManager


class AlertManager:
    """告警管理器"""
    
    def __init__(self, config_path: str = None):
        self.config_manager = ConfigManager(config_path)
        self.config = self.config_manager.get_all()
        
        # 告警配置
        alert_config = self.config.get("alert", {})
        self.enabled = alert_config.get("enabled", False)
        self.cooldown_minutes = alert_config.get("cooldown_minutes", 60)
        self.aggregation_minutes = alert_config.get("aggregation_minutes", 5)
        
        # 告警历史
        self.alerts_history: List[Dict] = []
        self.alerts_file = Path("alerts.json")
    
    def send_alert(self, anomaly: Dict) -> Dict:
        """发送告警
        
        Args:
            anomaly: 异常信息
        
        Returns:
            发送结果
        """
        # 检查是否启用
        if not self.enabled:
            return {
                "sent": False,
                "reason": "告警功能已disabled"
            }
        
        # 检查冷却期
        if self._is_in_cooldown(anomaly):
            return {
                "sent": False,
                "reason": f"告警在冷却期内（{self.cooldown_minutes}分钟）"
            }
        
        # 检查聚合窗口
        if self._should_aggregate(anomaly):
            return {
                "sent": False,
                "reason": f"告警在聚合窗口内（{self.aggregation_minutes}分钟）"
            }
        
        # 发送告警（这里简化为记录到文件）
        alert_record = {
            **anomaly,
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
        
        self.alerts_history.append(alert_record)
        self._save_alerts()
        
        return {
            "sent": True,
            "reason": "告警已发送",
            "alert": alert_record
        }
    
    def _is_in_cooldown(self, anomaly: Dict) -> bool:
        """检查是否在冷却期"""
        if not self.alerts_history:
            return False
        
        # 查找相同类型的最后一次告警
        for alert in reversed(self.alerts_history):
            if alert.get("type") == anomaly.get("type"):
                last_sent = datetime.fromisoformat(alert["sent_at"])
                cooldown_end = last_sent + timedelta(minutes=self.cooldown_minutes)
                
                if datetime.now() < cooldown_end:
                    return True
        
        return False
    
    def _should_aggregate(self, anomaly: Dict) -> bool:
        """检查是否应该聚合"""
        if not self.alerts_history:
            return False
        
        # 查找最近聚合窗口内的告警
        for alert in reversed(self.alerts_history):
            last_sent = datetime.fromisoformat(alert["sent_at"])
            aggregation_end = last_sent + timedelta(minutes=self.aggregation_minutes)
            
            if datetime.now() < aggregation_end:
                return True
        
        return False
    
    def _save_alerts(self):
        """保存告警历史"""
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts_history, f, indent=2, ensure_ascii=False)
    
    def get_stats(self) -> Dict:
        """获取告警统计"""
        return {
            "total_alerts": len(self.alerts_history),
            "enabled": self.enabled,
            "cooldown_minutes": self.cooldown_minutes,
            "aggregation_minutes": self.aggregation_minutes
        }
