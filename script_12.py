# 列出所有创建的文件
import os

files = [
    "main.c",
    "main.h", 
    "yaskawa.c",
    "yaskawa.h",
    "stm32f4xx_it.c",
    "stm32f4xx_it.h",
    "stm32f4xx_hal_conf.h",
    "system_stm32f4xx.c",
    "startup_stm32f407xx.s",
    "STM32F407VGTx_FLASH.ld",
    "Makefile",
    "README.md"
]

print("STM32F407 Yaskawa编码器通信项目文件列表：")
print("="*50)

for i, filename in enumerate(files, 1):
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print(f"{i:2d}. {filename:<25} ({size:,} bytes)")
    else:
        print(f"{i:2d}. {filename:<25} (不存在)")

print("\n项目结构说明：")
print("- 核心源文件: main.c, yaskawa.c")
print("- 头文件: *.h") 
print("- 系统文件: system_stm32f4xx.c, startup_stm32f407xx.s")
print("- 中断处理: stm32f4xx_it.c")
print("- 配置文件: stm32f4xx_hal_conf.h")
print("- 链接脚本: STM32F407VGTx_FLASH.ld")
print("- 构建脚本: Makefile")
print("- 文档: README.md")

print(f"\n总共创建了 {len(files)} 个文件")
print("\n编译命令：")
print("  make simple   # 简化版本（无需HAL库）")
print("  make all      # 完整版本（需要HAL库）")
print("  make flash    # 烧录程序")
print("  make clean    # 清理文件")
print("  make help     # 查看帮助")