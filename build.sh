#!/bin/bash
# STM32F407 Yaskawa编码器项目快速构建脚本

echo "STM32F407 Yaskawa编码器项目构建脚本"
echo "=================================="

# 检查工具链
echo "1. 检查ARM GCC工具链..."
if ! command -v arm-none-eabi-gcc &> /dev/null; then
    echo "错误: 未找到arm-none-eabi-gcc"
    echo "请安装ARM GCC工具链"
    exit 1
fi

echo "   找到 arm-none-eabi-gcc: $(arm-none-eabi-gcc --version | head -n1)"

# 检查Make
echo "2. 检查Make工具..."
if ! command -v make &> /dev/null; then
    echo "错误: 未找到make"
    echo "请安装Make工具"
    exit 1
fi

echo "   找到 make: $(make --version | head -n1)"

# 清理旧文件
echo "3. 清理旧的构建文件..."
make clean > /dev/null 2>&1

# 编译项目
echo "4. 编译项目..."
if make simple; then
    echo "✓ 编译成功!"
    echo "生成的文件:"
    ls -la build/
else
    echo "✗ 编译失败!"
    exit 1
fi

echo ""
echo "构建完成! 可以使用以下命令烧录:"
echo "  make flash          # 使用st-flash烧录"
echo "  make openocd-flash  # 使用OpenOCD烧录"
echo ""
echo "使用串口工具监控输出(115200, 8N1):"
echo "  PC2 -> USB转TTL模块RX"
echo "  GND -> USB转TTL模块GND"
