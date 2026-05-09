# Copyright (c) 2026 思捷娅科技 (SJYKJ)
# 浪费模式定义文件
# 每个模式：name, description, threshold, detection_rule

# 模式1：重复查询
declare -gA PATTERN_DUPLICATE_QUERY=(
  [name]="重复查询"
  [desc]="相同prompt多次调用"
  [threshold]="3"
  [rule]="same_prompt_count >= 3"
  [severity]="medium"
  [suggestion]="使用缓存或记忆系统，避免重复查询相同内容"
)

# 模式2：过长上下文
declare -gA PATTERN_LONG_CONTEXT=(
  [name]="过长上下文"
  [desc]="上下文>80%窗口仍继续"
  [threshold]="80"
  [rule]="context_usage_pct > 80"
  [severity]="high"
  [suggestion]="达到80%上下文窗口时自动切换新会话，减少token浪费"
)

# 模式3：无效重试
declare -gA PATTERN_INVALID_RETRY=(
  [name]="无效重试"
  [desc]="连续3+次相同错误"
  [threshold]="3"
  [rule]="consecutive_same_error >= 3"
  [severity]="high"
  [suggestion]="检测相同错误模式后切换策略，而非重复尝试"
)

# 模式4：过度生成
declare -gA PATTERN_OVER_GENERATION=(
  [name]="过度生成"
  [desc]="输出远超预期长度"
  [threshold]="5000"
  [rule]="output_tokens > 5000 && output_tokens > 3*input_tokens"
  [severity]="medium"
  [suggestion]="在prompt中明确指定输出长度限制"
)

# 模式5：低质量循环
declare -gA PATTERN_LOW_QUALITY_LOOP=(
  [name]="低质量循环"
  [desc]="输出评分持续低于阈值"
  [threshold]="0.5"
  [rule]="quality_score < 0.5 for 3+ consecutive"
  [severity]="critical"
  [suggestion]="检测到质量下降趋势时，重置上下文并尝试不同方法"
)
