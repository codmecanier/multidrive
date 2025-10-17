# 创建yaskawa.c源文件
yaskawa_c_content = '''
#include "yaskawa.h"
#include <string.h>
#include <math.h>

// 全局变量
static yaskawa_handle_t yaskawa_handle = {0};

// DMA句柄
DMA_HandleTypeDef hdma_tx;
DMA_HandleTypeDef hdma_rx;
TIM_HandleTypeDef htim_tx;
TIM_HandleTypeDef htim_rx;

void yaskawa_init(void)
{
    if (yaskawa_handle.initialized) {
        return;
    }
    
    // 硬件初始化
    yaskawa_hw_init();
    
    // 构建Manchester编码的请求数据
    yaskawa_build_request();
    
    yaskawa_handle.initialized = true;
}

void yaskawa_hw_init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    DMA_InitTypeDef DMA_InitStruct = {0};
    TIM_TimeBaseInitTypeDef TIM_TimeBaseStructure = {0};
    
    // 使能时钟
    __HAL_RCC_TIM8_CLK_ENABLE();
    __HAL_RCC_TIM2_CLK_ENABLE();
    __HAL_RCC_DMA1_CLK_ENABLE();
    __HAL_RCC_DMA2_CLK_ENABLE();
    
    // TX定时器配置 (TIM8)
    htim_tx.Instance = TIM8;
    htim_tx.Init.Prescaler = 0;
    htim_tx.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim_tx.Init.Period = 20;  // 168MHz / (20+1) = 8MHz
    htim_tx.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    htim_tx.Init.RepetitionCounter = 0;
    HAL_TIM_Base_Init(&htim_tx);
    
    // RX定时器配置 (TIM2)
    htim_rx.Instance = TIM2;
    htim_rx.Init.Prescaler = 0;
    htim_rx.Init.CounterMode = TIM_COUNTERMODE_UP;
    htim_rx.Init.Period = 0xFFFFFFFF;
    htim_rx.Init.ClockDivision = TIM_CLOCKDIVISION_DIV1;
    HAL_TIM_Base_Init(&htim_rx);
    
    // 配置TIM2的输入捕获
    TIM_IC_InitTypeDef sConfigIC = {0};
    sConfigIC.ICPolarity = TIM_INPUTCHANNELPOLARITY_BOTHEDGE;
    sConfigIC.ICSelection = TIM_ICSELECTION_DIRECTTI;
    sConfigIC.ICPrescaler = TIM_ICPSC_DIV1;
    sConfigIC.ICFilter = 0;
    HAL_TIM_IC_ConfigChannel(&htim_rx, &sConfigIC, TIM_CHANNEL_4);
    
    // TX DMA配置
    hdma_tx.Instance = DMA2_Stream1;
    hdma_tx.Init.Channel = DMA_CHANNEL_7;
    hdma_tx.Init.Direction = DMA_MEMORY_TO_PERIPH;
    hdma_tx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_tx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_tx.Init.PeriphDataAlignment = DMA_PDATAALIGN_WORD;
    hdma_tx.Init.MemDataAlignment = DMA_MDATAALIGN_WORD;
    hdma_tx.Init.Mode = DMA_NORMAL;
    hdma_tx.Init.Priority = DMA_PRIORITY_VERY_HIGH;
    hdma_tx.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    HAL_DMA_Init(&hdma_tx);
    
    // RX DMA配置
    hdma_rx.Instance = DMA1_Stream7;
    hdma_rx.Init.Channel = DMA_CHANNEL_3;
    hdma_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_rx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_rx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_rx.Init.PeriphDataAlignment = DMA_PDATAALIGN_HALFWORD;
    hdma_rx.Init.MemDataAlignment = DMA_MDATAALIGN_HALFWORD;
    hdma_rx.Init.Mode = DMA_NORMAL;
    hdma_rx.Init.Priority = DMA_PRIORITY_VERY_HIGH;
    hdma_rx.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    HAL_DMA_Init(&hdma_rx);
}

void yaskawa_build_request(void)
{
    // Manchester编码的请求字符串
    // 同步信号 + HDLC帧格式
    const char request[] = "0101010101010101010 01111110 111110 111110 111110 1 01111110";
    char manchester_encoded[sizeof(request) * 2];
    
    uint32_t tim_high = YASKAWA_TX_PIN << 16;  // 设置引脚
    uint32_t tim_low = YASKAWA_TX_PIN;         // 复位引脚
    
    // Manchester编码: 0->01, 1->10
    int j = 0;
    for(int i = 0; request[i]; i++) {
        if(request[i] == '0') {
            manchester_encoded[j++] = '0';
            manchester_encoded[j++] = '1';
        } else if(request[i] == '1') {
            manchester_encoded[j++] = '1';
            manchester_encoded[j++] = '0';
        }
    }
    manchester_encoded[j] = '\\0';
    
    // 构建DMA传输缓冲区
    yaskawa_handle.tx_buffer_pos = 0;
    for(int i = 0; manchester_encoded[i]; i++) {
        if(manchester_encoded[i] == '0') {
            yaskawa_handle.txbuf[yaskawa_handle.tx_buffer_pos++] = tim_high;
        } else if(manchester_encoded[i] == '1') {
            yaskawa_handle.txbuf[yaskawa_handle.tx_buffer_pos++] = tim_low;
        }
    }
    
    // 添加结束位
    yaskawa_handle.txbuf[yaskawa_handle.tx_buffer_pos++] = tim_high;
    yaskawa_handle.txbuf[yaskawa_handle.tx_buffer_pos++] = tim_high;
}

void yaskawa_update(void)
{
    if (!yaskawa_handle.initialized) {
        return;
    }
    
    // 等待上一次操作完成
    while(TIM2->CNT < 3300) {
        // 等待
    }
    
    // 启动发送
    yaskawa_start_transmission();
    
    // 等待发送完成
    while(!(DMA2->LISR & DMA_FLAG_TCIF1)) {
        // 等待发送完成
    }
    
    // 启动接收
    yaskawa_start_reception();
    
    // 等待一段时间让接收完成
    HAL_Delay(10);
    
    // 处理接收到的数据
    yaskawa_process_received_data();
}

void yaskawa_start_transmission(void)
{
    // 使能发送
    HAL_GPIO_WritePin(YASKAWA_TXEN_PORT, YASKAWA_TXEN_PIN, GPIO_PIN_SET);
    
    // 配置GPIO为输出模式
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = YASKAWA_TX_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(YASKAWA_TX_PORT, &GPIO_InitStruct);
    
    // 停止定时器
    TIM8->CR1 &= ~TIM_CR1_CEN;
    
    // 重新配置DMA
    HAL_DMA_DeInit(&hdma_tx);
    hdma_tx.Init.PeriphBaseAddr = (uint32_t)&YASKAWA_TX_PORT->BSRR;
    hdma_tx.Init.MemoryBaseAddr = (uint32_t)yaskawa_handle.txbuf;
    hdma_tx.Init.BufferSize = yaskawa_handle.tx_buffer_pos;
    HAL_DMA_Init(&hdma_tx);
    
    // 启动DMA传输
    HAL_DMA_Start(&hdma_tx, (uint32_t)yaskawa_handle.txbuf, 
                  (uint32_t)&YASKAWA_TX_PORT->BSRR, yaskawa_handle.tx_buffer_pos);
    
    // 配置定时器DMA请求
    TIM8->DIER = TIM_DIER_UDE;
    TIM8->CNT = 0;
    TIM8->CR1 |= TIM_CR1_CEN;
}

void yaskawa_start_reception(void)
{
    // 禁用发送
    HAL_GPIO_WritePin(YASKAWA_TXEN_PORT, YASKAWA_TXEN_PIN, GPIO_PIN_RESET);
    
    // 配置GPIO为复用功能模式
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    GPIO_InitStruct.Pin = YASKAWA_RX_PIN;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF1_TIM2;
    HAL_GPIO_Init(YASKAWA_RX_PORT, &GPIO_InitStruct);
    
    // 重新配置接收DMA
    HAL_DMA_DeInit(&hdma_rx);
    hdma_rx.Init.PeriphBaseAddr = (uint32_t)&TIM2->CCR4;
    hdma_rx.Init.MemoryBaseAddr = (uint32_t)yaskawa_handle.timer_data;
    hdma_rx.Init.BufferSize = YASKAWA_TIM_DATA_SIZE;
    HAL_DMA_Init(&hdma_rx);
    
    // 启动接收DMA
    HAL_DMA_Start(&hdma_rx, (uint32_t)&TIM2->CCR4, 
                  (uint32_t)yaskawa_handle.timer_data, YASKAWA_TIM_DATA_SIZE);
    
    // 配置定时器
    TIM2->CR1 &= ~TIM_CR1_CEN;
    TIM2->CCMR2 = TIM_CCMR2_CC4S_0;  // CC4映射到TI4
    TIM2->CCER = TIM_CCER_CC4E | TIM_CCER_CC4P | TIM_CCER_CC4NP;  // 双边沿触发
    TIM2->ARR = 0xFFFFFFFF;
    TIM2->DIER = TIM_DIER_CC4DE;  // CC4 DMA请求
    TIM2->CNT = 0;
    TIM2->CCR4 = 0;
    TIM2->CR1 |= TIM_CR1_CEN;
}

void yaskawa_process_received_data(void)
{
    int count = YASKAWA_TIM_DATA_SIZE - DMA1_Stream7->NDTR;
    
    if (count < 80) {
        yaskawa_handle.error_count++;
        return;
    }
    
    // 清空回复缓冲区
    memset((void*)yaskawa_handle.reply_data, 0, YASKAWA_REPLY_SIZE);
    
    // Manchester解码
    int read_counter = 0;
    int bit_counter = 0;
    int pol = 0;
    
    // 寻找同步模式
    for(int i = 1; i < count - 1; i++) {
        if(yaskawa_handle.timer_data[i + 1] - yaskawa_handle.timer_data[i] < MANCHESTER_BIT_TIME) {
            bit_counter++;
        } else if(bit_counter == 10) {
            read_counter = i + 1;
            pol = 0;
            break;
        } else {
            bit_counter = 0;
        }
    }
    
    if (read_counter == 0) {
        yaskawa_handle.error_count++;
        return;
    }
    
    // 解码数据位
    int write_counter = 0;
    int consecutive_ones = 0;
    
    for(int i = read_counter; i < count - 1 && write_counter < YASKAWA_DATA_BUFFER_SIZE - 1; i++) {
        if(yaskawa_handle.timer_data[i + 1] - yaskawa_handle.timer_data[i] < MANCHESTER_BIT_TIME) {
            i++; // 跳过短脉冲对中的第二个
            if(i >= count - 1) break;
            
            if(yaskawa_handle.timer_data[i + 1] - yaskawa_handle.timer_data[i] < MANCHESTER_BIT_TIME) {
                // 短-短: 无效
                yaskawa_handle.error_count++;
                return;
            } else {
                // 短-长: 数据位
                pol = 1 - pol;
            }
        } else {
            // 长脉冲: 极性变化
            pol = 1 - pol;
        }
        
        if(pol == 1) {
            consecutive_ones++;
            yaskawa_handle.manchester_data[write_counter] = '1';
            if(write_counter < YASKAWA_REPLY_SIZE * 8) {
                yaskawa_handle.reply_data[write_counter / 8] |= 1 << (7 - (write_counter % 8));
            }
            write_counter++;
        } else if(consecutive_ones == 5) {
            // 位填充: 忽略这个0
            consecutive_ones = 0;
        } else if(consecutive_ones == 6) {
            // HDLC标志: 结束
            yaskawa_handle.manchester_data[write_counter++] = 'H';
            break;
        } else {
            consecutive_ones = 0;
            yaskawa_handle.manchester_data[write_counter++] = '0';
        }
    }
    
    yaskawa_handle.manchester_data[write_counter] = '\\0';
    
    // CRC校验
    if (write_counter >= YASKAWA_REPLY_SIZE * 8) {
        yaskawa_crc16_t received_crc = (yaskawa_handle.reply_data[13] & 0xFF) | 
                                      (yaskawa_handle.reply_data[12] << 8);
        yaskawa_crc16_t calculated_crc = yaskawa_crc16_init();
        calculated_crc = yaskawa_crc16_update(calculated_crc, yaskawa_handle.reply_data, 12);
        calculated_crc = yaskawa_crc16_finalize(calculated_crc);
        
        if (received_crc == calculated_crc) {
            yaskawa_handle.crc_ok_count++;
            
            // 提取位置数据 (假设在前15位，偏移64位)
            uint32_t pos_raw = 0;
            for(int i = 0; i < 15; i++) {
                if(yaskawa_handle.manchester_data[i + 64] == '1') {
                    pos_raw |= (1 << i);
                }
            }
            
            // 转换为弧度 (-π 到 π)
            yaskawa_handle.position = (float)pos_raw / (float)(1 << 15) * 2.0f * M_PI - M_PI;
        } else {
            yaskawa_handle.crc_error_count++;
        }
    }
}

// CRC16实现 (简化版)
yaskawa_crc16_t yaskawa_crc16_init(void)
{
    return 0xFFFF;
}

yaskawa_crc16_t yaskawa_crc16_update(yaskawa_crc16_t crc, const uint8_t *data, uint16_t len)
{
    for (uint16_t i = 0; i < len; i++) {
        crc ^= data[i];
        for (int j = 0; j < 8; j++) {
            if (crc & 1) {
                crc = (crc >> 1) ^ 0xA001;
            } else {
                crc = crc >> 1;
            }
        }
    }
    return crc;
}

yaskawa_crc16_t yaskawa_crc16_finalize(yaskawa_crc16_t crc)
{
    return crc;
}

// 公开接口函数
float yaskawa_get_position(void)
{
    return yaskawa_handle.position;
}

uint32_t yaskawa_get_error_count(void)
{
    return yaskawa_handle.error_count;
}

uint32_t yaskawa_get_crc_ok(void)
{
    return yaskawa_handle.crc_ok_count;
}

uint32_t yaskawa_get_crc_error(void)
{
    return yaskawa_handle.crc_error_count;
}
'''

with open("yaskawa.c", "w") as f:
    f.write(yaskawa_c_content)

print("yaskawa.c文件已创建")