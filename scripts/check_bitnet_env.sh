#!/bin/bash
# BitNet集成测试脚本 - 检查环境和依赖

set -e

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

echo "================================"
echo "BitNet集成环境检查"
echo "================================"
echo

# 1. 检查CPU架构
log_step "1. 检查CPU架构..."
ARCH=$(uname -m)
if [ "$ARCH" = "x86_64" ]; then
    log_info "CPU架构：x86_64 ✅"
    # 检查AVX2支持
    if grep -q avx2 /proc/cpuinfo; then
        log_info "AVX2支持：✅"
    else
        log_warn "AVX2支持：❌（性能可能降低）"
    fi
elif [ "$ARCH" = "aarch64" ]; then
    log_info "CPU架构：ARM64 ✅"
else
    log_error "不支持的CPU架构：$ARCH"
fi
echo

# 2. 检查内存
log_step "2. 检查内存..."
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
AVAIL_MEM=$(free -g | awk '/^Mem:/{print $7}')

if [ "$TOTAL_MEM" -ge 8 ]; then
    log_info "总内存：${TOTAL_MEM}GB ✅"
else
    log_warn "总内存：${TOTAL_MEM}GB ⚠️（推荐8GB+）"
fi

if [ "$AVAIL_MEM" -ge 4 ]; then
    log_info "可用内存：${AVAIL_MEM}GB ✅"
else
    log_warn "可用内存：${AVAIL_MEM}GB ⚠️（推荐4GB+）"
fi
echo

# 3. 检查磁盘空间
log_step "3. 检查磁盘空间..."
DISK_AVAIL=$(df -BG /root | awk 'NR==2 {print $4}' | sed 's/G//')

if [ "$DISK_AVAIL" -ge 20 ]; then
    log_info "可用磁盘：${DISK_AVAIL}GB ✅"
else
    log_warn "可用磁盘：${DISK_AVAIL}GB ⚠️（推荐20GB+）"
fi
echo

# 4. 检查Python
log_step "4. 检查Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 9 ]; then
        log_info "Python版本：$PYTHON_VERSION ✅"
    else
        log_error "Python版本：$PYTHON_VERSION ❌（需要>=3.9）"
    fi
else
    log_error "Python未安装 ❌"
fi
echo

# 5. 检查CMake
log_step "5. 检查CMake..."
if command -v cmake &> /dev/null; then
    CMAKE_VERSION=$(cmake --version | head -1 | awk '{print $3}')
    CMAKE_MAJOR=$(echo $CMAKE_VERSION | cut -d. -f1)
    CMAKE_MINOR=$(echo $CMAKE_VERSION | cut -d. -f2)
    
    if [ "$CMAKE_MAJOR" -ge 3 ] && [ "$CMAKE_MINOR" -ge 22 ]; then
        log_info "CMake版本：$CMAKE_VERSION ✅"
    else
        log_warn "CMake版本：$CMAKE_VERSION ⚠️（需要>=3.22）"
    fi
else
    log_warn "CMake未安装 ⚠️（需要安装）"
fi
echo

# 6. 检查Clang
log_step "6. 检查Clang..."
if command -v clang &> /dev/null; then
    CLANG_VERSION=$(clang --version | head -1 | awk '{print $4}')
    CLANG_MAJOR=$(echo $CLANG_VERSION | cut -d. -f1)
    
    if [ "$CLANG_MAJOR" -ge 18 ]; then
        log_info "Clang版本：$CLANG_VERSION ✅"
    else
        log_warn "Clang版本：$CLANG_VERSION ⚠️（需要>=18）"
    fi
else
    log_warn "Clang未安装 ⚠️（需要安装）"
fi
echo

# 7. 检查Conda
log_step "7. 检查Conda..."
if command -v conda &> /dev/null; then
    CONDA_VERSION=$(conda --version | awk '{print $2}')
    log_info "Conda版本：$CONDA_VERSION ✅"
else
    log_warn "Conda未安装 ⚠️（推荐安装）"
fi
echo

# 8. 检查Git
log_step "8. 检查Git..."
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    log_info "Git版本：$GIT_VERSION ✅"
else
    log_error "Git未安装 ❌"
fi
echo

# 9. 检查网络
log_step "9. 检查网络连接..."
if ping -c 1 github.com &> /dev/null; then
    log_info "网络连接：✅"
else
    log_warn "网络连接：❌（离线模式可用）"
fi
echo

# 10. 总结
echo "================================"
echo "环境检查总结"
echo "================================"
echo

log_info "推荐配置："
echo "- CPU：x86_64 with AVX2"
echo "- 内存：8GB+"
echo "- 磁盘：20GB+"
echo "- Python：3.9+"
echo "- CMake：3.22+"
echo "- Clang：18+"
echo

log_info "下一步："
echo "1. 安装缺失的依赖"
echo "2. 克隆BitNet仓库"
echo "3. 下载模型"
echo "4. 构建项目"
echo

log_info "安装命令："
echo "# 安装Clang"
echo "bash -c \"\$(wget -O - https://apt.llvm.org/llvm.sh)\""
echo
echo "# 安装CMake"
echo "pip install cmake"
echo
echo "# 创建Conda环境"
echo "conda create -n bitnet-cpp python=3.9"
echo "conda activate bitnet-cpp"
