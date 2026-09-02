# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
#!/usr/bin/env python3
"""
支付方式检查器 (Payment Checker)
v7.5.6 - 2026-07-13

功能：
1. 自动识别 Issue 中的支付方式（crypto/fiat/platform/RTC）
2. 验证钱包地址格式
3. 检查是否支持该支付方式
4. 输出支付可行性报告

使用：
    python3 payment_checker.py <owner/repo> <issue_number>
    python3 payment_checker.py --scan-results <file>

版权：MIT License | Copyright (c) 2026 思捷娅科技 (SJYKJ)
"""

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class PaymentType(Enum):
    CRYPTO = "crypto"
    FIAT = "fiat"
    PLATFORM = "platform"
    RTC = "rtc"
    UNKNOWN = "unknown"


@dataclass
class PaymentInfo:
    """支付方式信息"""
    type: PaymentType = PaymentType.UNKNOWN
    token: str = ""
    wallet: str = ""
    method: str = ""
    currency: str = ""
    platform: str = ""
    amount: str = ""
    raw_text: str = ""
    confidence: float = 0.0
    warnings: list = field(default_factory=list)


class PaymentChecker:
    """支付方式检查器"""

    # 支持的加密货币
    SUPPORTED_CRYPTO = ["USDT", "USDC", "ETH", "BTC", "SOL", "TRX"]

    # 支持的链
    SUPPORTED_CHAINS = ["TRC20", "ERC20", "BEP20", "SPL", "BTC"]

    # 支持的法币支付方式
    SUPPORTED_FIAT = ["PayPal", "Wise", "Bank Transfer", "Stripe", "Alipay", "WeChat Pay"]

    # 支持的平台
    SUPPORTED_PLATFORMS = ["Algora", "UbiquityOS", "Gitcoin", "Bountysource", "Superteam"]

    # 钱包地址正则
    WALLET_PATTERNS = {
        "ETH": r"0x[a-fA-F0-9]{40}",
        "TRC20": r"T[a-zA-Z0-9]{33}",
        "BTC": r"[13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[a-zA-HJ-NP-Z0-9]{25,62}",
        "SOL": r"[1-9A-HJ-NP-Za-km-z]{32,44}",
        "USDT": r"0x[a-fA-F0-9]{40}|T[a-zA-Z0-9]{33}",
    }

    def __init__(self):
        self.supported_methods = self._load_supported_methods()
        self.user_wallets = self._load_user_wallets()

    def _load_supported_methods(self) -> dict:
        """加载支持的支付方式（从配置或环境变量）"""
        return {
            "crypto": {
                "tokens": os.getenv("SUPPORTED_TOKENS", "USDT,USDC,ETH,BTC").split(","),
                "chains": os.getenv("SUPPORTED_CHAINS", "TRC20,ERC20,BEP20").split(","),
            },
            "fiat": {
                "methods": os.getenv("SUPPORTED_FIAT_METHODS", "PayPal,Wise,Bank Transfer").split(","),
                "currencies": os.getenv("SUPPORTED_CURRENCIES", "USD,EUR,CNY").split(","),
            },
            "platform": {
                "platforms": os.getenv("SUPPORTED_PLATFORMS", "Algora,UbiquityOS,Gitcoin").split(","),
            },
            "rtc": {
                "min_amount": float(os.getenv("RTC_MIN_AMOUNT", "10")),
                "network": os.getenv("RTC_NETWORK", "rustchain"),
            },
        }

    def _load_user_wallets(self) -> dict:
        """加载用户配置的钱包地址"""
        wallets = {}

        # 从环境变量读取
        wallets["USDT_TRC20"] = os.getenv("USDT_WALLET_TRC20", "")
        wallets["USDT_ERC20"] = os.getenv("USDT_WALLET_ERC20", "")
        wallets["ETH"] = os.getenv("ETH_WALLET", "")
        wallets["BTC"] = os.getenv("BTC_WALLET", "")
        wallets["SOL"] = os.getenv("SOL_WALLET", "")
        wallets["RTC"] = os.getenv("RTC_WALLET", "")
        wallets["PAYPAL"] = os.getenv("PAYPAL_EMAIL", "")

        # 从 .env 文件读取（如果环境变量未设置）
        env_file = os.path.expanduser("~/.openclaw/workspace/skills/github-bounty-hunter/.env")
        if os.path.exists(env_file):
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip("\"'")
                        if key not in wallets or not wallets[key]:
                            wallets[key] = value

        return {k: v for k, v in wallets.items() if v}

    def check_issue_payment(self, owner_repo: str, issue_number: str) -> PaymentInfo:
        """检查指定 Issue 的支付方式"""
        # 获取 Issue 信息
        issue_data = self._fetch_issue(owner_repo, issue_number)
        if not issue_data:
            return PaymentInfo(warnings=[f"无法获取 Issue #{issue_number}"])

        # 获取评论
        comments = self._fetch_comments(owner_repo, issue_number)

        # 合并文本
        full_text = issue_data.get("body", "") + "\n" + "\n".join(
            c.get("body", "") for c in comments
        )

        return self._analyze_payment(full_text, issue_data)

    def _fetch_issue(self, owner_repo: str, issue_number: str) -> Optional[dict]:
        """通过 gh CLI 获取 Issue"""
        try:
            result = subprocess.run(
                ["gh", "issue", "view", issue_number, "--repo", owner_repo, "--json",
                 "title,body,number,author,labels,state,closed,mergedAt"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                return json.loads(result.stdout)
        except Exception as e:
            print(f"⚠️ 获取 Issue 失败: {e}", file=sys.stderr)
        return None

    def _fetch_comments(self, owner_repo: str, issue_number: str) -> list:
        """获取 Issue 评论"""
        try:
            result = subprocess.run(
                ["gh", "issue", "view", issue_number, "--repo", owner_repo, "--comments",
                 "--json", "body,author"],
                capture_output=True, text=True, timeout=30
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data.get("comments", [])
        except Exception:
            pass
        return []

    def _analyze_payment(self, text: str, issue_data: Optional[dict] = None) -> PaymentInfo:
        """分析文本中的支付方式信息"""
        info = PaymentInfo(raw_text=text[:500])

        # 1. 检查加密货币支付
        crypto_result = self._check_crypto(text)
        if crypto_result:
            info.type = PaymentType.CRYPTO
            info.token = crypto_result["token"]
            info.wallet = crypto_result["wallet"]
            info.confidence = crypto_result["confidence"]
            info.warnings = crypto_result.get("warnings", [])

        # 2. 检查 RTC 支付
        elif self._check_rtc(text):
            info.type = PaymentType.RTC
            info.amount = self._extract_amount(text)
            info.confidence = 0.9
            info.warnings = ["确认 RustChain 付款流程"]

        # 3. 检查法币支付
        elif self._check_fiat(text):
            info.type = PaymentType.FIAT
            fiat_result = self._check_fiat(text)
            info.method = fiat_result["method"]
            info.currency = fiat_result.get("currency", "USD")
            info.confidence = fiat_result["confidence"]

        # 4. 检查平台支付
        elif self._check_platform(text, issue_data):
            info.type = PaymentType.PLATFORM
            info.platform = self._check_platform(text, issue_data)["platform"]
            info.confidence = 0.85

        # 5. 未明确支付方式
        else:
            info.type = PaymentType.UNKNOWN
            info.confidence = 0.0
            info.warnings.append("⚠️ 支付方式未明确，建议查看评论或询问维护者")

        # 验证钱包地址（如果是 crypto）
        if info.type == PaymentType.CRYPTO and info.wallet:
            validation = self._validate_wallet(info.token, info.wallet)
            if not validation["valid"]:
                info.warnings.append(f"⚠️ 钱包地址格式无效: {validation['error']}")

        # 检查是否支持该支付方式
        support_check = self._is_supported(info)
        if not support_check["supported"]:
            info.warnings.append(f"❌ 不支持该支付方式: {support_check['reason']}")
        else:
            info.warnings.append(f"✅ 支持该支付方式")

        return info

    def _check_crypto(self, text: str) -> Optional[dict]:
        """检查加密货币支付信息"""
        text_lower = text.lower()

        # 查找 token 关键词
        for token in self.SUPPORTED_CRYPTO:
            if token.lower() in text_lower:
                # 查找钱包地址
                wallet = self._extract_wallet(text, token)
                if wallet:
                    return {
                        "token": token,
                        "wallet": wallet,
                        "confidence": 0.9,
                        "warnings": []
                    }
                else:
                    return {
                        "token": token,
                        "wallet": "",
                        "confidence": 0.5,
                        "warnings": [f"提到 {token} 但未提供钱包地址"]
                    }

        # 检查通用 crypto 关键词
        crypto_keywords = ["crypto payment", "crypto pay", "cryptocurrency", "wallet address"]
        for keyword in crypto_keywords:
            if keyword in text_lower:
                wallet = self._extract_wallet(text)
                if wallet:
                    return {
                        "token": "Unknown Crypto",
                        "wallet": wallet,
                        "confidence": 0.6,
                        "warnings": ["未指定具体代币"]
                    }

        return None

    def _check_rtc(self, text: str) -> bool:
        """检查 RTC 支付"""
        rtc_patterns = [
            r"\d+\s*RTC",
            r"reward.*\d+.*RTC",
            r"bounty.*\d+.*RTC",
            r"rustchain.*reward",
            r"payment.*rustchain",
        ]
        for pattern in rtc_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False

    def _check_fiat(self, text: str) -> Optional[dict]:
        """检查法币支付"""
        text_lower = text.lower()

        for method in self.SUPPORTED_FIAT:
            if method.lower() in text_lower:
                currency = self._extract_currency(text)
                return {
                    "method": method,
                    "currency": currency or "USD",
                    "confidence": 0.8,
                }

        # 检查法币金额模式
        fiat_amount = re.search(r"\$\d+(?:\.\d+)?", text)
        if fiat_amount:
            # 有美元金额但未指定支付方式
            return {
                "method": "Unspecified Fiat",
                "currency": "USD",
                "confidence": 0.4,
            }

        return None

    def _check_platform(self, text: str, issue_data: Optional[dict] = None) -> Optional[dict]:
        """检查平台支付"""
        text_lower = text.lower()

        for platform in self.SUPPORTED_PLATFORMS:
            if platform.lower() in text_lower:
                return {"platform": platform}

        # 检查 issue labels
        if issue_data:
            labels = [l.get("name", "").lower() for l in issue_data.get("labels", [])]
            for label in labels:
                for platform in self.SUPPORTED_PLATFORMS:
                    if platform.lower() in label:
                        return {"platform": platform}

        return None

    def _extract_wallet(self, text: str, token: str = "") -> str:
        """提取钱包地址"""
        # 根据 token 选择正则
        if token:
            patterns = [self.WALLET_PATTERNS.get(token, r"0x[a-fA-F0-9]{40}")]
        else:
            patterns = list(self.WALLET_PATTERNS.values())

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0)

        return ""

    def _extract_amount(self, text: str) -> str:
        """提取金额"""
        patterns = [
            r"\$\s*(\d+(?:,\d+)*(?:\.\d+)?)",
            r"(\d+(?:,\d+)*)\s*(?:USDT|USDC|USD)",
            r"(\d+)\s*RTC",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return ""

    def _extract_currency(self, text: str) -> Optional[str]:
        """提取货币类型"""
        currencies = ["USD", "EUR", "CNY", "GBP", "JPY"]
        text_upper = text.upper()
        for currency in currencies:
            if currency in text_upper:
                return currency
        return None

    def _validate_wallet(self, token: str, wallet: str) -> dict:
        """验证钱包地址格式"""
        token_upper = token.upper()

        # TRC20 USDT
        if token_upper == "USDT":
            if re.match(self.WALLET_PATTERNS["TRC20"], wallet):
                return {"valid": True, "chain": "TRC20"}
            elif re.match(self.WALLET_PATTERNS["ETH"], wallet):
                return {"valid": True, "chain": "ERC20"}
            else:
                return {"valid": False, "error": "不是有效的 USDT 地址 (TRC20/ERC20)"}

        # 其他 token
        pattern = self.WALLET_PATTERNS.get(token_upper)
        if pattern and re.match(pattern, wallet):
            return {"valid": True}

        return {"valid": False, "error": f"不是有效的 {token} 地址"}

    def _is_supported(self, info: PaymentInfo) -> dict:
        """检查是否支持该支付方式"""
        if info.type == PaymentType.CRYPTO:
            if info.token in self.supported_methods["crypto"]["tokens"]:
                return {"supported": True}
            return {"supported": False, "reason": f"不支持 {info.token}"}

        elif info.type == PaymentType.FIAT:
            if info.method in self.supported_methods["fiat"]["methods"]:
                return {"supported": True}
            return {"supported": False, "reason": f"不支持 {info.method}"}

        elif info.type == PaymentType.PLATFORM:
            if info.platform in self.supported_methods["platform"]["platforms"]:
                return {"supported": True}
            return {"supported": False, "reason": f"不支持平台 {info.platform}"}

        elif info.type == PaymentType.RTC:
            return {"supported": True}

        return {"supported": False, "reason": "支付方式未识别"}

    def format_report(self, info: PaymentInfo, owner_repo: str, issue_number: str) -> str:
        """格式化支付可行性报告"""
        type_icons = {
            PaymentType.CRYPTO: "💰",
            PaymentType.FIAT: "💵",
            PaymentType.PLATFORM: "🏦",
            PaymentType.RTC: "🔶",
            PaymentType.UNKNOWN: "❓",
        }

        icon = type_icons.get(info.type, "❓")

        report = f"""## 💳 支付方式检查报告

**Issue**: {owner_repo}#{issue_number}
**类型**: {icon} {info.type.value}
**置信度**: {info.confidence:.0%}"""

        if info.type == PaymentType.CRYPTO:
            report += f"""

**代币**: {info.token}
**钱包**: `{info.wallet[:8]}...{info.wallet[-4:] if info.wallet else '未提供'}`
**链**: {self._detect_chain(info.wallet)}"""

        elif info.type == PaymentType.FIAT:
            report += f"""

**方式**: {info.method}
**货币**: {info.currency}"""

        elif info.type == PaymentType.PLATFORM:
            report += f"""

**平台**: {info.platform}"""

        elif info.type == PaymentType.RTC:
            report += f"""

**金额**: {info.amount} RTC
**网络**: RustChain"""

        if info.warnings:
            report += "\n\n**警告/建议**:\n"
            for w in info.warnings:
                report += f"- {w}\n"

        # 用户配置的钱包
        if info.type == PaymentType.CRYPTO and self.user_wallets:
            report += "\n\n**你的钱包配置**:\n"
            for key, wallet in self.user_wallets.items():
                masked = f"`{wallet[:8]}...{wallet[-4:]}`" if len(wallet) > 12 else "`(未配置)`"
                report += f"- {key}: {masked}\n"

        return report

    def _detect_chain(self, wallet: str) -> str:
        """检测钱包链"""
        if wallet.startswith("0x"):
            return "ERC20"
        elif wallet.startswith("T"):
            return "TRC20"
        elif wallet.startswith("bc1") or wallet.startswith("1") or wallet.startswith("3"):
            return "BTC"
        return "Unknown"


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: python3 payment_checker.py <owner/repo> <issue_number>")
        print("      python3 payment_checker.py --scan-results <file>")
        sys.exit(1)

    checker = PaymentChecker()

    if sys.argv[1] == "--scan-results":
        # 从扫描结果文件批量检查
        results_file = sys.argv[2]
        with open(results_file) as f:
            content = f.read()

        # 提取 issue URLs
        issues = re.findall(r"(https://github\.com/([^/]+/[^/]+)/issues/(\d+))", content)
        for url, owner_repo, issue_num in issues:
            print(f"\n{'='*60}")
            print(f"检查 {owner_repo}#{issue_num}")
            print(f"{'='*60}")

            info = checker.check_issue_payment(owner_repo, issue_num)
            report = checker.format_report(info, owner_repo, issue_num)
            print(report)

    else:
        # 单个 Issue 检查
        owner_repo = sys.argv[1]
        issue_number = sys.argv[2] if len(sys.argv) > 2 else ""

        info = checker.check_issue_payment(owner_repo, issue_number)
        report = checker.format_report(info, owner_repo, issue_number)
        print(report)

        # 如果不支持，退出码 1
        if info.type == PaymentType.UNKNOWN:
            sys.exit(1)


if __name__ == "__main__":
    main()
