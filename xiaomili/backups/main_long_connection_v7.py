#!/usr/bin/env python3
"""飞书中继服务 - 长连接版本"""

import asyncio
import logging
from datetime import datetime
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/opt/feishu-relay/logs/relay-long-connection.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 导入配置
from config import (
    XIAOMILA_APP_ID,
    XIAOMILA_APP_SECRET,
    XIAOMILI_APP_ID,
    XIAOMILI_APP_SECRET
)

# 导入lark-oapi
try:
    import lark_oapi as lark
    logger.info("✅ lark-oapi SDK导入成功")
except ImportError as e:
    logger.error(f"❌ lark-oapi SDK导入失败: {e}")
    logger.error("请安装: pip3 install lark-oapi")
    exit(1)


class FeishuLongConnection:
    """飞书长连接服务"""
    
    def __init__(self, app_id: str, app_secret: str, bot_name: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.bot_name = bot_name
        
        # 创建事件分发器
        self.dispatcher = lark.EventDispatcherHandler.builder(
            "",  # encrypt_key（可选）
            "",  # verification_token（可选）
        ).register_p2_im_message_receive_v1(self.handle_message).build()
        
        # 创建WebSocket客户端
        self.ws_client = None
        
        logger.info(f"初始化{bot_name}长连接服务...")
    
    def handle_message(self, event):
        """处理消息接收事件（P1ImMessageReceiveV1）"""
        try:
            logger.info(f"[{self.bot_name}] 收到消息事件")
            
            # 解析事件数据
            message = event.event.message
            sender = event.event.sender
            
            logger.info(f"[{self.bot_name}] 消息内容: {message.content}")
            logger.info(f"[{self.bot_name}] 发送者: {sender.sender_id.open_id}")
            
            # TODO: 存储到数据库
            # TODO: 路由消息
            # TODO: 自动回复
            
        except Exception as e:
            logger.error(f"[{self.bot_name}] 处理消息失败: {e}", exc_info=True)
    
    def start(self):
        """启动长连接"""
        try:
            logger.info(f"[{self.bot_name}] 正在建立长连接...")
            
            # 创建WebSocket客户端
            self.ws_client = lark.ws.Client(
                app_id=self.app_id,
                app_secret=self.app_secret,
                event_handler=self.dispatcher,
                log_level=lark.LogLevel.INFO
            )
            
            # 启动长连接
            self.ws_client.start()
            
            logger.info(f"[{self.bot_name}] ✅ 长连接已建立")
            
        except Exception as e:
            logger.error(f"[{self.bot_name}] ❌ 建立长连接失败: {e}", exc_info=True)
            raise
    
    def stop(self):
        """停止长连接"""
        if self.ws_client:
            self.ws_client.stop()
            logger.info(f"[{self.bot_name}] ⏹️ 长连接已停止")


def main():
    """主函数"""
    logger.info("=" * 60)
    logger.info("启动飞书中继服务（长连接版本）...")
    logger.info("=" * 60)
    
    # 创建小米粒的长连接服务
    xiaomili_service = FeishuLongConnection(
        app_id=XIAOMILI_APP_ID,
        app_secret=XIAOMILI_APP_SECRET,
        bot_name="小米粒"
    )
    
    try:
        # 启动长连接
        xiaomili_service.start()
        
        logger.info("=" * 60)
        logger.info("✅ 飞书中继服务已启动（长连接模式）")
        logger.info("=" * 60)
        
        # 保持运行
        import time
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("收到停止信号...")
        xiaomili_service.stop()
        logger.info("服务已停止")
    except Exception as e:
        logger.error(f"服务运行错误: {e}", exc_info=True)
        xiaomili_service.stop()


if __name__ == "__main__":
    main()
