# STM32F407 Yaskawa编码器通信项目

这个项目实现了在STM32F407微控制器上与Yaskawa伺服编码器进行串行通信的功能。项目基于正点原子探索者STM32F407开发板设计，使用Manchester编码和HDLC协议进行数据传输。

## 硬件连接

### 引脚配置
- **PG8**: 收发控制引脚（RS485方向控制）
- **PA2**: UART4_TX，用于数据发送
- **PA3**: UART4_RX，用于数据接收（同时用于编码器数据输入）
- **PC2**: UART4串口输出到电脑（用于调试）

### 连接示意图
```
STM32F407开发板        Yaskawa编码器
    PG8    ---------> 收发控制
    PA2    ---------> 数据发送线
    PA3    <--------- 数据接收线
    GND    ---------> 地线
```

### 调试连接
```
STM32F407开发板        USB转TTL模块        电脑
    PC2    ---------> RX               串口监视器
    GND    ---------> GND              (115200波特率)
```

## 软件特性

- **Manchester编码**: 实现0/1数据的双相编码
- **HDLC协议**: 使用帧同步和CRC校验
- **实时数据读取**: 100ms刷新率输出编码器位置
- **错误检测**: CRC校验和通信错误统计
- **串口调试**: 通过UART输出调试信息

## 项目结构

```
yaskawa_encoder/
├── main.c                    # 主程序文件
├── yaskawa.c/.h             # Yaskawa编码器通信模块
├── stm32f4xx_it.c/.h        # 中断处理文件
├── stm32f4xx_hal_conf.h     # HAL库配置
├── system_stm32f4xx.c       # 系统初始化
├── startup_stm32f407xx.s    # 启动文件
├── STM32F407VGTx_FLASH.ld   # 链接脚本
├── Makefile                 # 构建脚本
└── README.md                # 本文件
```

## 编译环境要求

### 必需工具
1. **ARM GCC工具链**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install gcc-arm-none-eabi

   # Windows
   # 下载ARM GCC工具链并添加到PATH
   ```

2. **Make工具**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install make

   # Windows
   # 安装MinGW或使用MSYS2
   ```

3. **烧录工具** (选择其一)
   - st-flash (推荐)
   - OpenOCD
   - STM32 ST-LINK Utility

### 可选库文件
- STM32F4xx HAL库 (用于完整功能)

## 编译和烧录

### 快速编译（简化版本）
```bash
# 编译项目（不需要HAL库）
make simple

# 或者完整编译（需要HAL库）
make all
```

### 烧录程序
```bash
# 使用st-flash烧录
make flash

# 或使用OpenOCD烧录
make openocd-flash
```

### 清理构建文件
```bash
make clean
```

### 查看帮助
```bash
make help
```

## 使用方法

1. **硬件连接**: 按照上述引脚配置连接STM32和Yaskawa编码器

2. **编译程序**:
   ```bash
   make simple    # 简化版本
   # 或
   make all       # 完整版本
   ```

3. **烧录程序**:
   ```bash
   make flash
   ```

4. **串口监控**: 
   - 连接USB转TTL模块到PC2(TX)和GND
   - 打开串口工具(如PuTTY, minicom等)
   - 设置波特率115200, 8N1
   - 观察编码器数据输出

## 输出格式

程序每100ms输出一次编码器数据：
```
STM32F407 Yaskawa Encoder Reader Started
Pos: 0.123456 rad, Errors: 0, CRC OK: 1250, CRC Err: 2
Pos: 0.234567 rad, Errors: 0, CRC OK: 1251, CRC Err: 2
...
```

输出字段说明：
- **Pos**: 编码器位置（弧度）
- **Errors**: 通信错误次数
- **CRC OK**: CRC校验成功次数
- **CRC Err**: CRC校验失败次数

## 功能说明

### Manchester编码
- 0位编码为01序列
- 1位编码为10序列
- 提供时钟恢复能力

### HDLC协议
- 使用0x7E作为帧标志
- 支持位填充（连续5个1后插入0）  
- CRC16校验保证数据完整性

### 定时器和DMA
- TIM8: 用于发送时序控制
- TIM2: 用于接收边沿捕获
- DMA: 高效数据传输，减少CPU负载

## 故障排除

### 编译错误
1. **找不到arm-none-eabi-gcc**:
   - 确保ARM GCC工具链已安装并添加到PATH

2. **HAL库相关错误**:
   - 使用`make simple`编译简化版本
   - 或下载STM32F4xx HAL库到项目目录

### 运行问题
1. **无串口输出**:
   - 检查UART连接和波特率设置
   - 确认PC2引脚连接正确

2. **编码器数据异常**:
   - 检查PG8, PA2, PA3引脚连接
   - 确认编码器供电正常
   - 检查地线连接

3. **通信错误率高**:
   - 检查信号线长度和屏蔽
   - 确认时序参数设置
   - 检查电源噪声

## 开发和调试

### GDB调试
```bash
# 启动GDB调试
make debug
```

### 修改配置
主要配置参数在`yaskawa.h`中：
- `MANCHESTER_BIT_TIME`: Manchester位时间
- `YASKAWA_DATA_BUFFER_SIZE`: 数据缓冲区大小
- 各种GPIO和定时器定义

### 扩展功能
1. 添加更多编码器类型支持
2. 实现多轴编码器读取
3. 添加网络接口输出
4. 集成到更大的控制系统

## 参考资料

- [STM32F407 Reference Manual](https://www.st.com/resource/en/reference_manual/dm00031020.pdf)
- [Yaskawa Servo系列文档](https://www.yaskawa.com)
- [Manchester编码原理](https://en.wikipedia.org/wiki/Manchester_code)
- [HDLC协议规范](https://tools.ietf.org/html/rfc1662)

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 作者

- 项目适配：Andrew (基于原始Yaskawa通信代码)
- 目标平台：正点原子探索者STM32F407开发板
- 开发时间：2025年10月

## 联系方式

如有问题或建议，请通过以下方式联系：
- GitHub Issues
- 邮件联系

---

**注意**: 本项目为教育和学习目的，请在实际工业应用中进行充分测试和验证。
