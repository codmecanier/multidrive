@echo off
REM STM32F407 Yaskawa编码器项目快速构建脚本 (Windows)

echo STM32F407 Yaskawa编码器项目构建脚本 (Windows)
echo ==================================================

REM 检查工具链
echo 1. 检查ARM GCC工具链...
arm-none-eabi-gcc --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到arm-none-eabi-gcc
    echo 请安装ARM GCC工具链并添加到PATH
    pause
    exit /b 1
)

echo    找到 arm-none-eabi-gcc

REM 检查Make  
echo 2. 检查Make工具...
make --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到make
    echo 请安装Make工具(MinGW或MSYS2)
    pause
    exit /b 1
)

echo    找到 make

REM 清理旧文件
echo 3. 清理旧的构建文件...
make clean >nul 2>&1

REM 编译项目
echo 4. 编译项目...
make simple
if errorlevel 1 (
    echo 编译失败!
    pause
    exit /b 1
)

echo.
echo 编译成功! 生成的文件:
dir build

echo.
echo 构建完成! 可以使用以下命令烧录:
echo   make flash          # 使用st-flash烧录
echo   make openocd-flash  # 使用OpenOCD烧录
echo.
echo 使用串口工具监控输出(115200, 8N1):
echo   PC2 -^> USB转TTL模块RX  
echo   GND -^> USB转TTL模块GND
pause
