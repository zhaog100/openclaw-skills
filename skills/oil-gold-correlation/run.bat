@echo off
REM oil-gold-correlation 跨平台启动脚本 (Windows)
REM 用法: run.bat {fetch|analyze|visualize|report|advisor|all}
chcp 65001 >nul
set SCRIPT_DIR=%~dp0

REM 优先检测 conda
where conda >nul 2>&1 && (
    call conda activate oil-gold 2>nul || goto :fallback
) || goto :fallback

:run
python "%SCRIPT_DIR%scripts\main.py" %*
goto :eof

:fallback
where python3 >nul 2>&1 && (
    python3 "%SCRIPT_DIR%scripts\main.py" %*
) || (
    echo ❌ 未找到 Python 环境，请安装 Miniconda 后重试
    echo    https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)