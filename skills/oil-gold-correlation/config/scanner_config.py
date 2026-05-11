"""
机会扫描器配置文件
将硬编码阈值抽离到配置文件，提高可维护性
"""

# 价差阈值配置
GAP_THRESHOLDS = {
    "gap_5_threshold": 1.5,        # 5日价差阈值(%)
    "gap_30_threshold": 3.0,       # 30日价差阈值(%)
}

# 技术指标阈值
TECHNICAL_THRESHOLDS = {
    "i5_threshold": -1.0,          # 5日指标阈值
    "z_score_threshold": 1.0,      # 标准化分数阈值
    "rsi_overbought": 70,          # RSI超买阈值
    "rsi_oversold": 30,            # RSI超卖阈值
}

# 置信度配置
CONFIDENCE_CONFIG = {
    "min_confidence": 70,          # 最低置信度(%)
    "base_confidence": 50,         # 基础置信度
    "gap_multiplier": 10,          # 价差乘数
    "max_confidence": 85,          # 最高置信度
}

# 影响分数配置  
SCORE_IMPACT = {
    "trend_up": 3,                 # 趋势向上
    "trend_down": -3,              # 趋势向下
    "volume_spike": 5,             # 成交量激增
    "volume_decline": -5,          # 成交量下降
    "divergence": -10,             # 背离信号
    "reversal": 8,                 # 反转信号
    "breakout": 15,                # 突破信号
    "support_break": -15,          # 支撑位突破
}

# 相关性阈值
CORRELATION_THRESHOLDS = {
    "strong_correlation": 0.5,     # 强相关阈值
    "medium_correlation": 0.3,     # 中等相关阈值
    "weak_correlation": 0.1,       # 弱相关阈值
}

# 波动率阈值
VOLATILITY_THRESHOLDS = {
    "high_volatility": 0.3,        # 高波动率阈值
    "medium_volatility": 0.15,     # 中等波动率阈值
    "low_volatility": 0.05,        # 低波动率阈值
}

# 交叉验证配置
VALIDATION_CONFIG = {
    "price_diff_threshold": 0.02,  # 价格差异阈值(2%)
    "min_sources": 2,              # 最小数据源数量
}


def get_scanner_config():
    """获取扫描器配置"""
    return {
        "gap_thresholds": GAP_THRESHOLDS,
        "technical_thresholds": TECHNICAL_THRESHOLDS,
        "confidence_config": CONFIDENCE_CONFIG,
        "score_impact": SCORE_IMPACT,
        "correlation_thresholds": CORRELATION_THRESHOLDS,
        "volatility_thresholds": VOLATILITY_THRESHOLDS,
        "validation_config": VALIDATION_CONFIG,
    }


def get_confidence_formula():
    """获取置信度计算公式说明"""
    return {
        "formula": "min(base_confidence + gap_5 * gap_multiplier, max_confidence)",
        "description": "置信度 = 基础值 + 价差 × 乘数，最高不超过最大值",
        "parameters": {
            "base_confidence": "基础置信度(50%)",
            "gap_multiplier": "价差权重(10)",
            "max_confidence": "置信度上限(85%)"
        }
    }