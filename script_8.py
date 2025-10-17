# 修正main.c文件
main_c_fixed = '''
#include "stm32f4xx_hal.h"
#include "yaskawa.h"
#include <stdio.h>
#include <string.h>

// 系统时钟配置
void SystemClock_Config(void);
void MX_GPIO_Init(void);
void MX_UART4_Init(void);
void Error_Handler(void);

UART_HandleTypeDef huart4;

int main(void)
{
    // HAL库初始化
    HAL_Init();
    
    // 配置系统时钟
    SystemClock_Config();
    
    // 初始化GPIO
    MX_GPIO_Init();
    
    // 初始化UART4
    MX_UART4_Init();
    
    // 初始化Yaskawa编码器通信
    yaskawa_init();
    
    char msg[] = "STM32F407 Yaskawa Encoder Reader Started\\r\\n";
    HAL_UART_Transmit(&huart4, (uint8_t*)msg, strlen(msg), 1000);
    
    while (1)
    {
        // 更新编码器数据
        yaskawa_update();
        
        // 获取编码器位置
        float position = yaskawa_get_position();
        uint32_t error_count = yaskawa_get_error_count();
        uint32_t crc_ok = yaskawa_get_crc_ok();
        uint32_t crc_error = yaskawa_get_crc_error();
        
        // 通过串口输出编码器数据
        char buffer[200];
        snprintf(buffer, sizeof(buffer), 
                "Pos: %.6f rad, Errors: %lu, CRC OK: %lu, CRC Err: %lu\\r\\n", 
                position, error_count, crc_ok, crc_error);
        
        HAL_UART_Transmit(&huart4, (uint8_t*)buffer, strlen(buffer), 1000);
        
        HAL_Delay(100); // 100ms刷新率
    }
}

void SystemClock_Config(void)
{
    RCC_OscInitTypeDef RCC_OscInitStruct = {0};
    RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

    // 配置电源
    __HAL_RCC_PWR_CLK_ENABLE();
    __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

    // 配置HSE时钟
    RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
    RCC_OscInitStruct.HSEState = RCC_HSE_ON;
    RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
    RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
    RCC_OscInitStruct.PLL.PLLM = 8;  // 8MHz / 8 = 1MHz
    RCC_OscInitStruct.PLL.PLLN = 336; // 1MHz * 336 = 336MHz
    RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2; // 336MHz / 2 = 168MHz
    RCC_OscInitStruct.PLL.PLLQ = 7;  // 336MHz / 7 = 48MHz (USB)
    if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK) {
        Error_Handler();
    }

    // 配置系统时钟
    RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                                |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
    RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
    RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;   // 168MHz
    RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;    // 42MHz
    RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;    // 84MHz
    if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK) {
        Error_Handler();
    }
}

void MX_UART4_Init(void)
{
    huart4.Instance = UART4;
    huart4.Init.BaudRate = 115200;
    huart4.Init.WordLength = UART_WORDLENGTH_8B;
    huart4.Init.StopBits = UART_STOPBITS_1;
    huart4.Init.Parity = UART_PARITY_NONE;
    huart4.Init.Mode = UART_MODE_TX_RX;
    huart4.Init.HwFlowCtl = UART_HWCONTROL_NONE;
    huart4.Init.OverSampling = UART_OVERSAMPLING_16;
    if (HAL_UART_Init(&huart4) != HAL_OK) {
        Error_Handler();
    }
}

void MX_GPIO_Init(void)
{
    GPIO_InitTypeDef GPIO_InitStruct = {0};

    // 使能GPIO时钟
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOC_CLK_ENABLE();
    __HAL_RCC_GPIOG_CLK_ENABLE();

    // 配置PA2为UART4_TX
    GPIO_InitStruct.Pin = GPIO_PIN_2;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF8_UART4;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    // 配置PA3为UART4_RX  
    GPIO_InitStruct.Pin = GPIO_PIN_3;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF8_UART4;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    // 配置PG8为收发控制引脚
    GPIO_InitStruct.Pin = GPIO_PIN_8;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);
    
    // 初始状态设为接收模式
    HAL_GPIO_WritePin(GPIOG, GPIO_PIN_8, GPIO_PIN_RESET);
}

void Error_Handler(void)
{
    /* User can add his own implementation to report the HAL error return state */
    __disable_irq();
    while (1) {
        // 错误处理
    }
}

// 重定向printf到UART
int _write(int file, char *ptr, int len)
{
    HAL_UART_Transmit(&huart4, (uint8_t*)ptr, len, 1000);
    return len;
}

void HAL_UART_MspInit(UART_HandleTypeDef* huart)
{
    if(huart->Instance == UART4)
    {
        __HAL_RCC_UART4_CLK_ENABLE();
        __HAL_RCC_GPIOA_CLK_ENABLE();
    }
}

#ifdef USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
    /* User can add his own implementation to report the file name and line number,
       tex: printf("Wrong parameters value: file %s on line %d\\r\\n", file, line) */
}
#endif /* USE_FULL_ASSERT */
'''

with open("main.c", "w") as f:
    f.write(main_c_fixed)

print("main.c已修正")