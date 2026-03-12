#!/usr/bin/env python3
"""
BitNet推理封装 - 简化版
用于测试和演示BitNet本地推理能力
"""

import subprocess
import os
import sys
from typing import Optional

class BitNetInference:
    """BitNet推理接口"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        初始化BitNet推理接口
        
        Args:
            model_path: 模型路径（可选，默认使用2B模型）
        """
        self.workspace = "/root/.openclaw/workspace"
        self.bitnet_dir = os.path.join(self.workspace, "BitNet")
        
        if model_path:
            self.model_path = model_path
        else:
            # 默认使用2B模型
            self.model_path = os.path.join(
                self.bitnet_dir,
                "models/BitNet-b1.58-2B-4T/ggml-model-i2_s.gguf"
            )
        
        self.runner_path = os.path.join(
            self.bitnet_dir,
            "build/bin/bitnet-runner"
        )
    
    def check_environment(self) -> bool:
        """
        检查BitNet环境是否就绪
        
        Returns:
            bool: 环境是否就绪
        """
        if not os.path.exists(self.bitnet_dir):
            print(f"❌ BitNet目录不存在：{self.bitnet_dir}")
            return False
        
        if not os.path.exists(self.model_path):
            print(f"❌ 模型文件不存在：{self.model_path}")
            return False
        
        if not os.path.exists(self.runner_path):
            print(f"❌ 推理程序不存在：{self.runner_path}")
            return False
        
        print("✅ BitNet环境检查通过")
        return True
    
    def generate(
        self,
        prompt: str,
        max_tokens: int = 100,
        temperature: float = 0.7,
        top_p: float = 0.9,
        verbose: bool = False
    ) -> Optional[str]:
        """
        生成文本
        
        Args:
            prompt: 输入提示
            max_tokens: 最大生成token数
            temperature: 温度参数
            top_p: Top-p采样参数
            verbose: 是否显示详细信息
        
        Returns:
            生成的文本，失败返回None
        """
        if not self.check_environment():
            return None
        
        cmd = [
            self.runner_path,
            "--model", self.model_path,
            "--prompt", prompt,
            "--n-predict", str(max_tokens),
            "--temp", str(temperature),
            "--top-p", str(top_p)
        ]
        
        if verbose:
            print(f"🔧 执行命令：{' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60  # 60秒超时
            )
            
            if result.returncode != 0:
                print(f"❌ BitNet推理失败：{result.stderr}")
                return None
            
            if verbose:
                print(f"✅ 推理成功")
            
            return result.stdout.strip()
        
        except subprocess.TimeoutExpired:
            print(f"❌ BitNet推理超时（>{60}秒）")
            return None
        except Exception as e:
            print(f"❌ BitNet推理错误：{str(e)}")
            return None
    
    def test_simple(self) -> bool:
        """
        测试简单推理
        
        Returns:
            bool: 测试是否成功
        """
        print("================================")
        print("BitNet简单推理测试")
        print("================================")
        print()
        
        prompt = "Hello, BitNet! Please say 'Hello' back:"
        
        print(f"📝 提示：{prompt}")
        print()
        
        response = self.generate(prompt, max_tokens=20, verbose=True)
        
        if response:
            print()
            print(f"🤖 响应：{response}")
            print()
            print("✅ 测试成功！")
            return True
        else:
            print()
            print("❌ 测试失败！")
            return False


def main():
    """主函数"""
    print("BitNet推理封装 - 测试")
    print()
    
    # 创建推理接口
    bitnet = BitNetInference()
    
    # 检查环境
    if not bitnet.check_environment():
        print()
        print("❌ 环境检查失败，请先安装BitNet")
        print()
        print("安装步骤：")
        print("1. 克隆BitNet仓库")
        print("2. 下载模型")
        print("3. 构建项目")
        print()
        print("详细步骤请参考：docs/BITNET_INTEGRATION_PLAN.md")
        return 1
    
    # 运行测试
    if bitnet.test_simple():
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
