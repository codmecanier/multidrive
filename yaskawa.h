
#ifndef YASKAWA_H
#define YASKAWA_H

#include "stm32f4xx_hal.h"
#include <stdint.h>
#include <stdbool.h>

// Yaskawa编码器通信参数
#define YASKAWA_DATA_BUFFER_SIZE 150
#define YASKAWA_TIM_DATA_SIZE 300
#define YASKAWA_REPLY_SIZE 14

// Manchester编码参数
#define MANCHESTER_BIT_TIME 15  // 位时间

// GPIO引脚定义
#define YASKAWA_TXEN_PORT GPIOG
#define YASKAWA_TXEN_PIN GPIO_PIN_8
#define YASKAWA_TX_PORT GPIOA
#define YASKAWA_TX_PIN GPIO_PIN_2
#define YASKAWA_RX_PORT GPIOA
#define YASKAWA_RX_PIN GPIO_PIN_3

// 定时器定义
#define YASKAWA_TX_TIM TIM8
#define YASKAWA_RX_TIM TIM2

// DMA定义
#define YASKAWA_TX_DMA_STREAM DMA2_Stream1
#define YASKAWA_TX_DMA_CHANNEL DMA_CHANNEL_7
#define YASKAWA_RX_DMA_STREAM DMA1_Stream7
#define YASKAWA_RX_DMA_CHANNEL DMA_CHANNEL_3

// 结构体定义
typedef struct {
    volatile uint32_t txbuf[128];
    volatile char manchester_data[YASKAWA_DATA_BUFFER_SIZE];
    volatile uint16_t timer_data[YASKAWA_TIM_DATA_SIZE];
    uint8_t reply_data[YASKAWA_REPLY_SIZE];

    float position;
    uint32_t error_count;
    uint32_t crc_ok_count;
    uint32_t crc_error_count;

    bool initialized;
    uint32_t tx_buffer_pos;
} yaskawa_handle_t;

// CRC16计算相关
typedef uint16_t yaskawa_crc16_t;

// 函数声明
void yaskawa_init(void);
void yaskawa_update(void);
float yaskawa_get_position(void);
uint32_t yaskawa_get_error_count(void);
uint32_t yaskawa_get_crc_ok(void);
uint32_t yaskawa_get_crc_error(void);

// 内部函数声明
void yaskawa_hw_init(void);
void yaskawa_build_request(void);
void yaskawa_start_transmission(void);
void yaskawa_start_reception(void);
void yaskawa_process_received_data(void);
yaskawa_crc16_t yaskawa_crc16_init(void);
yaskawa_crc16_t yaskawa_crc16_update(yaskawa_crc16_t crc, const uint8_t *data, uint16_t len);
yaskawa_crc16_t yaskawa_crc16_finalize(yaskawa_crc16_t crc);

#endif // YASKAWA_H
