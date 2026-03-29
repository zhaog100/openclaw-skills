#!/usr/bin/env python3
"""
WattCoin Energy Monitor - 主程序
Raspberry Pi 能源监控解决方案

版权声明：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
GitHub: https://github.com/zhaog100/openclaw-skills
"""

import json
import time
import logging
import sqlite3
import hashlib
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path

# 配置
CONFIG_FILE = Path(__file__).parent / "config.json"
DB_FILE = Path(__file__).parent / "energy_data.db"
LOG_FILE = Path(__file__).parent / "wattcoin_energy.log"

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class Config:
    """配置管理"""
    
    def __init__(self):
        self.device_type = "mock"  # mock, kasa, shelly, usb
        self.device_ip = ""
        self.api_endpoint = "http://localhost:8000/api/v1/energy/report"
        self.polling_interval = 60  # 秒
        self.wallet_address = ""
        self.wallet_private_key = ""  # 仅用于签名，不上传
        self.mock_mode = True
        
        self.load()
    
    def load(self):
        """加载配置"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE) as f:
                data = json.load(f)
                self.device_type = data.get("device_type", "mock")
                self.device_ip = data.get("device_ip", "")
                self.api_endpoint = data.get("api_endpoint", "")
                self.polling_interval = data.get("polling_interval", 60)
                self.wallet_address = data.get("wallet_address", "")
                self.mock_mode = data.get("mock_mode", True)
                logger.info(f"配置已加载：{self.device_type}")
        else:
            logger.warning("配置文件不存在，使用默认配置")
            self.save()
    
    def save(self):
        """保存配置"""
        data = {
            "device_type": self.device_type,
            "device_ip": self.device_ip,
            "api_endpoint": self.api_endpoint,
            "polling_interval": self.polling_interval,
            "wallet_address": self.wallet_address,
            "mock_mode": self.mock_mode
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info("配置已保存")


class Database:
    """本地数据库"""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS energy_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp REAL,
                voltage REAL,
                current REAL,
                power REAL,
                energy_wh REAL,
                device_type TEXT,
                reported INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("数据库初始化完成")
    
    def insert(self, data: Dict[str, Any]):
        """插入数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO energy_data 
            (timestamp, voltage, current, power, energy_wh, device_type)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            data['timestamp'],
            data['voltage'],
            data['current'],
            data['power'],
            data['energy_wh'],
            data['device_type']
        ))
        
        conn.commit()
        conn.close()
    
    def get_unreported(self, limit: int = 100):
        """获取未报告的数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM energy_data 
            WHERE reported = 0 
            ORDER BY timestamp 
            LIMIT ?
        ''', (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return rows
    
    def mark_reported(self, ids: list):
        """标记为已报告"""
        if not ids:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(ids))
        cursor.execute(f'''
            UPDATE energy_data 
            SET reported = 1 
            WHERE id IN ({placeholders})
        ''', ids)
        
        conn.commit()
        conn.close()


class DeviceReader:
    """设备读取器"""
    
    def __init__(self, config: Config):
        self.config = config
    
    def read(self) -> Dict[str, Any]:
        """读取设备数据"""
        if self.config.mock_mode or self.config.device_type == "mock":
            return self._read_mock()
        elif self.config.device_type == "kasa":
            return self._read_kasa()
        elif self.config.device_type == "shelly":
            return self._read_shelly()
        elif self.config.device_type == "usb":
            return self._read_usb()
        else:
            return self._read_mock()
    
    def _read_mock(self) -> Dict[str, Any]:
        """Mock 模式（测试用）"""
        import random
        return {
            "voltage": 220 + random.uniform(-5, 5),
            "current": random.uniform(0.1, 5.0),
            "power": random.uniform(50, 500),
            "energy_wh": random.uniform(0.1, 10.0)
        }
    
    def _read_kasa(self) -> Dict[str, Any]:
        """读取 TP-Link Kasa 设备"""
        try:
            from kasa import SmartPlug
            import asyncio
            
            async def read():
                plug = SmartPlug(self.config.device_ip)
                await plug.update()
                return {
                    "voltage": plug.voltage,
                    "current": plug.current,
                    "power": plug.power,
                    "energy_wh": plug.emeter_today or 0
                }
            
            return asyncio.run(read())
        except Exception as e:
            logger.error(f"Kasa 读取失败：{e}")
            return self._read_mock()
    
    def _read_shelly(self) -> Dict[str, Any]:
        """读取 Shelly 设备"""
        try:
            url = f"http://{self.config.device_ip}/status"
            resp = requests.get(url, timeout=5)
            data = resp.json()
            
            return {
                "voltage": data.get('emeters', [{}])[0].get('voltage', 220),
                "current": data.get('emeters', [{}])[0].get('current', 0),
                "power": data.get('emeters', [{}])[0].get('power', 0),
                "energy_wh": data.get('emeters', [{}])[0].get('total', 0)
            }
        except Exception as e:
            logger.error(f"Shelly 读取失败：{e}")
            return self._read_mock()
    
    def _read_usb(self) -> Dict[str, Any]:
        """读取 USB 功率计"""
        # 需要根据具体设备实现
        return self._read_mock()


class WattCoinClient:
    """WattCoin API 客户端"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
    
    def sign_data(self, data: Dict[str, Any]) -> str:
        """签名数据"""
        # 简单签名示例（实际应使用 Solana wallet 签名）
        message = json.dumps(data, sort_keys=True)
        signature = hashlib.sha256(
            f"{message}{self.config.wallet_private_key}".encode()
        ).hexdigest()
        return signature
    
    def report(self, data: Dict[str, Any]) -> bool:
        """报告数据到 API"""
        if not self.config.api_endpoint:
            logger.warning("API 端点未配置")
            return False
        
        payload = {
            **data,
            "wallet": self.config.wallet_address,
            "signature": self.sign_data(data),
            "timestamp": time.time()
        }
        
        try:
            resp = self.session.post(
                self.config.api_endpoint,
                json=payload,
                timeout=10
            )
            
            if resp.status_code == 200:
                logger.info("数据报告成功")
                return True
            else:
                logger.error(f"API 返回错误：{resp.status_code}")
                return False
                
        except requests.RequestException as e:
            logger.error(f"API 请求失败：{e}")
            return False


class EnergyMonitor:
    """能源监控主类"""
    
    def __init__(self):
        self.config = Config()
        self.db = Database(DB_FILE)
        self.reader = DeviceReader(self.config)
        self.client = WattCoinClient(self.config)
        self.running = False
    
    def run_once(self):
        """运行一次监控"""
        # 读取数据
        data = self.reader.read()
        data['timestamp'] = time.time()
        data['device_type'] = self.config.device_type
        
        # 保存到本地
        self.db.insert(data)
        
        logger.info(f"读取数据：{data['power']:.2f}W")
        
        # 报告到 API
        if self.client.report(data):
            self.db.mark_reported([data['timestamp']])
    
    def run_loop(self):
        """运行监控循环"""
        self.running = True
        logger.info("启动能源监控...")
        
        while self.running:
            try:
                self.run_once()
            except Exception as e:
                logger.error(f"监控循环错误：{e}")
            
            time.sleep(self.config.polling_interval)
    
    def stop(self):
        """停止监控"""
        self.running = False
        logger.info("停止能源监控")


def main():
    """主函数"""
    monitor = EnergyMonitor()
    
    try:
        monitor.run_loop()
    except KeyboardInterrupt:
        logger.info("收到中断信号，停止服务")
        monitor.stop()


if __name__ == "__main__":
    main()
