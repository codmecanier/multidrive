# 创建硬件配置说明文件
hardware_config = '''# STM32F407 Yaskawa编码器硬件配置说明

## 引脚映射表

| 功能 | STM32引脚 | 复用功能 | 方向 | 说明 |
|------|-----------|----------|------|------|
| 收发控制 | PG8 | GPIO_OUT | 输出 | RS485方向控制，高电平发送 |
| 数据发送 | PA2 | UART4_TX | 输出 | Manchester编码数据输出 |  
| 数据接收 | PA3 | TIM2_CH4/UART4_RX | 输入 | 编码器数据输入，双边沿捕获 |
| 调试串口TX | PC2 | UART4_TX | 输出 | 调试信息输出到PC |
| 调试串口RX | PC3 | UART4_RX | 输入 | 可选，用于接收PC命令 |

## 时钟配置

```
外部晶振: 8MHz (HSE)
系统时钟: 168MHz (SYSCLK)
AHB时钟: 168MHz (HCLK) 
APB1时钟: 42MHz (PCLK1) - UART4, TIM2
APB2时钟: 84MHz (PCLK2) - TIM8
```

## 定时器配置

### TIM8 (发送定时器)
- 时钟源: APB2 (84MHz)
- 预分频: 0 
- 自动重载: 20
- 输出频率: 84MHz / (20+1) = 4MHz
- 用途: Manchester编码发送时序

### TIM2 (接收定时器)  
- 时钟源: APB1 (42MHz)
- 预分频: 0
- 自动重载: 0xFFFFFFFF  
- 输入捕获: 通道4，双边沿触发
- 用途: 接收信号边沿时间戳捕获

## DMA配置

### DMA2 Stream1 (发送DMA)
- 通道: 7 (TIM8_UP)
- 方向: 内存到外设
- 数据宽度: 32位
- 用途: 自动发送Manchester编码数据

### DMA1 Stream7 (接收DMA)
- 通道: 3 (TIM2_CH4) 
- 方向: 外设到内存
- 数据宽度: 16位
- 用途: 自动采集时间戳数据

## 电气特性

### 输入输出电平
- GPIO输出电平: 3.3V CMOS
- GPIO输入电平: 3.3V兼容，5V容忍
- 驱动能力: 25mA (高速模式)

### 信号完整性
- 建议信号线长度: < 3米
- 推荐使用屏蔽双绞线
- 地线连接: 必须可靠接地
- 终端电阻: 根据传输线阻抗匹配

## Manchester编码规范

### 编码规则
- 逻辑'0': 低->高跳变 (01)
- 逻辑'1': 高->低跳变 (10)  
- 位时间: 可配置，默认15个计数周期
- 同步模式: 前导码 + 数据 + 校验

### HDLC协议帧格式
```
开始标志 | 地址 | 控制 | 数据 | CRC16 | 结束标志
  0x7E   | ... | ... | ... | ..... |  0x7E
```

## 调试接口

### UART4调试串口
- 波特率: 115200
- 数据位: 8
- 停止位: 1  
- 校验位: 无
- 流控: 无

### SWD调试接口
- SWDIO: PA13
- SWCLK: PA14
- SWO: PB3 (可选)
- nRST: NRST

## 电源要求

### 供电电压
- VDD: 3.3V ±5%
- VDDA: 3.3V (模拟电源)
- VBAT: 3.3V (备份域)

### 功耗估算
- 运行模式: ~100mA @ 168MHz
- 低功耗模式: 可通过软件配置

## 机械尺寸

适用于正点原子探索者STM32F407开发板:
- PCB尺寸: 约100mm x 74mm  
- 插针间距: 2.54mm
- 安装孔: 4个M3螺丝孔

## 环境要求

### 工作温度
- 商业级: 0°C ~ +70°C
- 工业级: -40°C ~ +85°C

### 存储温度
- -65°C ~ +150°C

### 湿度
- 相对湿度: 10% ~ 90% (无凝露)

## 兼容性说明

### Yaskawa编码器型号
- Sigma系列编码器
- 串行通信接口
- 电压兼容: 5V/3.3V

### STM32F4系列兼容性  
- STM32F407xx: 完全兼容
- STM32F405xx: 兼容
- STM32F417xx: 兼容
- STM32F415xx: 兼容

## 注意事项

1. **电气连接**
   - 确保地线连接可靠
   - 避免长距离无屏蔽连接
   - 注意信号完整性

2. **软件配置**
   - 检查时钟配置正确性
   - 确认GPIO复用功能设置
   - 验证定时器参数

3. **调试建议**
   - 使用示波器观察信号
   - 监控串口输出信息
   - 检查CRC校验结果

4. **安全考虑**
   - 工业环境下注意防护
   - 避免静电损伤
   - 正确的设备接地
'''

with open("HARDWARE_CONFIG.md", "w", encoding='utf-8') as f:
    f.write(hardware_config)

print("硬件配置说明文件已创建: HARDWARE_CONFIG.md")

# 创建一个简单的构建脚本
build_script = '''#!/bin/bash
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
'''

with open("build.sh", "w") as f:
    f.write(build_script)

# 创建Windows批处理文件
build_bat = '''@echo off
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
'''

with open("build.bat", "w") as f:
    f.write(build_bat)

print("构建脚本已创建:")
print("- build.sh (Linux/macOS)")  
print("- build.bat (Windows)")

# 显示最终的项目文件统计
final_files = [
    "main.c", "main.h", "yaskawa.c", "yaskawa.h",
    "stm32f4xx_it.c", "stm32f4xx_it.h", "stm32f4xx_hal_conf.h",
    "system_stm32f4xx.c", "startup_stm32f407xx.s",
    "STM32F407VGTx_FLASH.ld", "Makefile", "README.md",
    "HARDWARE_CONFIG.md", "build.sh", "build.bat"
]

total_size = sum(os.path.getsize(f) for f in final_files if os.path.exists(f))

print(f"\n项目总结:")
print(f"- 总文件数: {len(final_files)}")
print(f"- 总大小: {total_size:,} bytes ({total_size/1024:.1f} KB)")
print(f"- 目标平台: STM32F407VGT6 (正点原子探索者开发板)")
print(f"- 功能: Yaskawa编码器串行通信")
print(f"- 编码方式: Manchester + HDLC协议")