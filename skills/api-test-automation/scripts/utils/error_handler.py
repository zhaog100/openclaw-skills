# Copyright (c) 2026 思捷娅科技 (SJYKJ) — MIT License
# Version: v1.6
"""
错误处理与友好化模块 — 将原始异常转换为用户可读的错误提示

功能：
- 异常分类与映射表（10+ 种常见异常类型）
- @handle_exceptions 装饰器（统一捕获、转换、日志记录）
- FriendlyError 自定义异常类
- 优雅降级（非致命错误不中断执行）
- 原始堆栈写入 logs/error.log（用户只看友好提示）

使用示例：
    from utils.error_handler import handle_exceptions, FriendlyError

    @handle_exceptions(operation="解析 OpenAPI 文档", resource=file_path)
    def parse_openapi(file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
        if 'paths' not in data:
            raise FriendlyError(
                message="文档缺少 paths 字段",
                suggestion="请确认上传的是有效的 OpenAPI 文档",
                error_code="MISSING_PATHS"
            )
        return data
"""

from __future__ import annotations

import json
import logging
import traceback
from functools import wraps
from pathlib import Path
from typing import Callable, TypeVar, Any, Optional

try:
    import yaml
except ImportError:
    yaml = None  # type: ignore[assignment]

# =====================================================================
# 日志配置
# =====================================================================

# 创建 logs 目录
_log_dir = Path("logs")
_log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(_log_dir / "error.log", encoding="utf-8"),
        logging.StreamHandler(),  # 同时输出到控制台
    ],
)
logger = logging.getLogger("api_test.error_handler")

# =====================================================================
# 自定义异常类
# =====================================================================


class FriendlyError(Exception):
    """用户可理解的友好错误类。

    Attributes:
        message: 用户可见的错误消息
        suggestion: 建议的修复步骤
        error_code: 错误代码（用于程序化处理）
    """

    def __init__(
        self,
        message: str,
        suggestion: str = "",
        error_code: str = "",
    ):
        self.message = message
        self.suggestion = suggestion
        self.error_code = error_code
        super().__init__(self.message)

    def __str__(self) -> str:
        msg = self.message
        if self.suggestion:
            msg += f"\n💡 建议: {self.suggestion}"
        return msg

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典，方便报告集成。"""
        return {
            "message": self.message,
            "suggestion": self.suggestion,
            "error_code": self.error_code,
        }


# =====================================================================
# 异常 → 友好消息映射表
# =====================================================================

_ERROR_MAP: dict[type, Callable[[Exception], dict[str, str]]] = {}


def register_error_handler(
    exc_type: type[Exception],
) -> Callable[[Callable[[Exception], dict[str, str]]], Callable[[Exception], dict[str, str]]]:
    """装饰器：注册异常类型到映射表。"""

    def decorator(func: Callable[[Exception], dict[str, str]]) -> Callable[[Exception], dict[str, str]]:
        _ERROR_MAP[exc_type] = func
        return func

    return decorator


# --- FileNotFoundError ---
@register_error_handler(FileNotFoundError)
def _handle_file_not_found(e: FileNotFoundError) -> dict[str, str]:
    return {
        "message": f"❌ 找不到文件：{e.filename}",
        "suggestion": "请检查文件路径是否正确，或重新上传文件",
    }


# --- json.JSONDecodeError ---
@register_error_handler(json.JSONDecodeError)
def _handle_json_decode_error(e: json.JSONDecodeError) -> dict[str, str]:
    return {
        "message": f"❌ 文件格式有误：不是合法的 JSON 格式 — {e.msg}",
        "suggestion": "请确认文件内容完整，或尝试转换为 YAML 格式重新上传",
    }


# --- yaml.YAMLError ---
if yaml is not None:
    @register_error_handler(yaml.YAMLError)
    def _handle_yaml_error(e: yaml.YAMLError) -> dict[str, str]:  # type: ignore[name-defined]
        return {
            "message": "❌ YAML 文件解析失败：格式有误",
            "suggestion": "请检查缩进是否正确，或转换为 JSON 格式重新上传",
        }


# --- KeyError (通用，但特别处理 paths/schemas) ---
@register_error_handler(KeyError)
def _handle_key_error(e: KeyError) -> dict[str, str]:
    key = str(e.args[0]) if e.args else "未知字段"
    if key == "paths":
        return {
            "message": "❌ 文档结构不完整：未能找到 `paths` 字段",
            "suggestion": "请确认上传的是有效的 OpenAPI/Swagger 文档",
        }
    if key == "schemas":
        return {
            "message": "⚠️ 文档缺少 `schemas` 字段：部分校验功能可能无法使用",
            "suggestion": "请确认上传的是完整的 OpenAPI 3.x 文档",
        }
    return {
        "message": f"❌ 文档结构不完整：缺少字段 `{key}`",
        "suggestion": "请检查文档格式是否符合规范",
    }


# --- httpx 相关异常 (懒加载，避免强依赖) ---
_httpx_handlers_registered: bool = False


def _register_httpx_handlers():
    """延迟导入 httpx 异常类型，避免无 httpx 时报错。"""
    global _httpx_handlers_registered

    if _httpx_handlers_registered:
        return

    try:
        import httpx

        @register_error_handler(httpx.ConnectTimeout)
        def _handle_connect_timeout(e: httpx.ConnectTimeout) -> dict[str, str]:
            return {
                "message": f"⏰ 连接超时：无法访问目标服务",
                "suggestion": "请确认：1) 服务是否正常运行  2) 网络是否连通  3) URL 是否正确",
            }

        @register_error_handler(httpx.TimeoutException)
        def _handle_request_timeout(e: httpx.TimeoutException) -> dict[str, str]:
            timeout_val = "?"
            if hasattr(e, "request") and e.request:
                timeout_val = str(e.request.timeout) if e.request.timeout else "?"
            return {
                "message": f"⏰ 响应超时：请求在 {timeout_val}s 内未完成",
                "suggestion": "请确认：1) 服务性能是否正常  2) 适当增加超时时间配置",
            }

        @register_error_handler(httpx.HTTPStatusError)
        def _handle_http_status(e: httpx.HTTPStatusError) -> dict[str, str]:
            return {
                "message": f"⚠️ 服务返回错误状态码：{e.response.status_code}",
                "suggestion": f"详情: {e.response.text[:200]}",
            }

        _httpx_handlers_registered = True
    except ImportError:
        # httpx 未安装，稍后注册
        pass


# --- PermissionError ---
@register_error_handler(PermissionError)
def _handle_permission_error(e: PermissionError) -> dict[str, str]:
    return {
        "message": f"❌ 权限不足：无法写入报告到 {e.filename or '目标路径'}",
        "suggestion": "请检查目录写入权限，或使用 sudo 运行",
    }


# =====================================================================
# 装饰器
# =====================================================================

F = TypeVar("F", bound=Callable[..., Any])


def handle_exceptions(
    operation: str = "",
    resource: str = "",
) -> Callable[[F], F]:
    """装饰器：统一捕获异常，转换为友好消息。

    Args:
        operation: 当前操作描述（如"解析 OpenAPI 文档"）
        resource: 涉及的资源（如文件名、URL）

    用法:
        @handle_exceptions(operation="解析文档", resource="openapi.json")
        def parse_doc(path):
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return func(*args, **kwargs)
            except FriendlyError:
                # 友好错误直接抛出，不做转换
                raise
            except Exception as e:
                # 记录原始堆栈到日志文件
                logger.error(
                    "操作: %s | 资源: %s | 异常: %s",
                    operation,
                    resource,
                    e,
                    exc_info=True,
                )

                # 获取 httpx handlers（如果可用）
                _register_httpx_handlers()

                # 按类型查找友好映射
                for exc_cls, handler in _ERROR_MAP.items():
                    if isinstance(e, exc_cls):
                        info = handler(e)
                        raise FriendlyError(
                            message=info["message"],
                            suggestion=info.get("suggestion", ""),
                            error_code=e.__class__.__name__,
                        ) from e

                # 兜底：未知异常
                raise FriendlyError(
                    message=f"❌ 执行 '{operation}' 时发生未知错误：{str(e)}",
                    suggestion="请检查日志文件 logs/error.log 获取详细信息，或联系技术支持",
                    error_code="UNKNOWN",
                ) from e

        return wrapper  # type: ignore[return-value]

    return decorator


# =====================================================================
# 上下文管理器：优雅降级
# =====================================================================

from contextlib import contextmanager


@contextmanager
def graceful_fallback(
    operation: str = "操作",
    fallback_result: Any = None,
):
    """上下文管理器：捕获异常并返回降级结果，不中断整体执行。

    用法:
        with graceful_fallback("解析配置", fallback_result={}):
            config = load_config("config.json")
        # 如果 load_config 出错，config 为 {}
    """
    try:
        yield
    except FriendlyError:
        # 友好错误仍然抛出
        raise
    except Exception as e:
        logger.warning(
            "优雅降级: '%s' 失败，使用 fallback 结果。原因: %s",
            operation,
            e,
        )
        # 返回 fallback_result（由调用者通过其他方式获取）
        # 这里只是记录日志，实际返回值由调用者决定
        raise


# =====================================================================
# 工具函数
# =====================================================================


def format_error_summary(errors: list[FriendlyError]) -> str:
    """汇总多个错误，生成可读的错误列表。

    用法:
        errors = [...]  # 收集到的 FriendlyError
        print(format_error_summary(errors))
    """
    if not errors:
        return "✅ 无错误"

    lines = [f"⚠️ 共发现 {len(errors)} 个问题："]
    for i, err in enumerate(errors, 1):
        lines.append(f"  {i}. {err.message}")
        if err.suggestion:
            lines.append(f"     建议: {err.suggestion}")
    return "\n".join(lines)


def log_and_continue(error: Exception, operation: str) -> None:
    """记录错误但不中断执行（用于逐个用例的场景）。

    用法:
        for tc in test_cases:
            try:
                run_test(tc)
            except Exception as e:
                log_and_continue(e, f"运行用例 {tc.name}")
                # 继续下一个用例
    """
    logger.error("用例执行失败 [%s]: %s", operation, error)
    # 调用者可在此处将错误追加到结果列表中


__all__ = [
    "FriendlyError",
    "handle_exceptions",
    "graceful_fallback",
    "format_error_summary",
    "log_and_continue",
    "logger",
]
