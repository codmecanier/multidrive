# 创建stm32f4xx_it.c中断处理文件
it_c_content = '''
#include "main.h"
#include "stm32f4xx_it.h"

/* External variables */
extern TIM_HandleTypeDef htim_tx;
extern TIM_HandleTypeDef htim_rx;
extern DMA_HandleTypeDef hdma_tx;
extern DMA_HandleTypeDef hdma_rx;

/******************************************************************************/
/*           Cortex-M4 Processor Interruption and Exception Handlers          */ 
/******************************************************************************/
/**
  * @brief This function handles Non maskable interrupt.
  */
void NMI_Handler(void)
{

}

/**
  * @brief This function handles Hard fault interrupt.
  */
void HardFault_Handler(void)
{
  while (1)
  {
  }
}

/**
  * @brief This function handles Memory management fault.
  */
void MemManage_Handler(void)
{
  while (1)
  {
  }
}

/**
  * @brief This function handles Pre-fetch fault, memory access fault.
  */
void BusFault_Handler(void)
{
  while (1)
  {
  }
}

/**
  * @brief This function handles Undefined instruction or illegal state.
  */
void UsageFault_Handler(void)
{
  while (1)
  {
  }
}

/**
  * @brief This function handles System service call via SWI instruction.
  */
void SVC_Handler(void)
{

}

/**
  * @brief This function handles Debug monitor.
  */
void DebugMon_Handler(void)
{

}

/**
  * @brief This function handles Pendable request for system service.
  */
void PendSV_Handler(void)
{

}

/**
  * @brief This function handles System tick timer.
  */
void SysTick_Handler(void)
{
  HAL_IncTick();
}

/******************************************************************************/
/* STM32F4xx Peripheral Interrupt Handlers                                    */
/* Add here the Interrupt Handlers for the used peripherals.                  */
/* For the available peripheral interrupt handler names,                      */
/* please refer to the startup file (startup_stm32f4xx.s).                    */
/******************************************************************************/

/**
  * @brief This function handles DMA1 stream7 global interrupt.
  */
void DMA1_Stream7_IRQHandler(void)
{
  HAL_DMA_IRQHandler(&hdma_rx);
}

/**
  * @brief This function handles DMA2 stream1 global interrupt.
  */
void DMA2_Stream1_IRQHandler(void)
{
  HAL_DMA_IRQHandler(&hdma_tx);
}

/**
  * @brief This function handles TIM8 update interrupt and TIM13 global interrupt.
  */
void TIM8_UP_TIM13_IRQHandler(void)
{
  HAL_TIM_IRQHandler(&htim_tx);
}

/**
  * @brief This function handles TIM2 global interrupt.
  */
void TIM2_IRQHandler(void)
{
  HAL_TIM_IRQHandler(&htim_rx);
}
'''

with open("stm32f4xx_it.c", "w") as f:
    f.write(it_c_content)

# 创建stm32f4xx_it.h头文件
it_h_content = '''
#ifndef __STM32F4xx_IT_H
#define __STM32F4xx_IT_H

#ifdef __cplusplus
 extern "C" {
#endif 

/* Includes ------------------------------------------------------------------*/
/* Exported types ------------------------------------------------------------*/
/* Exported constants --------------------------------------------------------*/
/* Exported macro ------------------------------------------------------------*/
/* Exported functions ------------------------------------------------------- */

void NMI_Handler(void);
void HardFault_Handler(void);
void MemManage_Handler(void);
void BusFault_Handler(void);
void UsageFault_Handler(void);
void SVC_Handler(void);
void DebugMon_Handler(void);
void PendSV_Handler(void);
void SysTick_Handler(void);
void DMA1_Stream7_IRQHandler(void);
void DMA2_Stream1_IRQHandler(void);
void TIM8_UP_TIM13_IRQHandler(void);
void TIM2_IRQHandler(void);

#ifdef __cplusplus
}
#endif

#endif /* __STM32F4xx_IT_H */
'''

with open("stm32f4xx_it.h", "w") as f:
    f.write(it_h_content)

# 创建main.h头文件
main_h_content = '''
#ifndef __MAIN_H
#define __MAIN_H

#ifdef __cplusplus
extern "C" {
#endif

/* Includes ------------------------------------------------------------------*/
#include "stm32f4xx_hal.h"

/* Private includes ----------------------------------------------------------*/

/* Exported types ------------------------------------------------------------*/

/* Exported constants --------------------------------------------------------*/

/* Exported macro ------------------------------------------------------------*/

/* Exported functions prototypes ---------------------------------------------*/
void Error_Handler(void);

/* Private defines -----------------------------------------------------------*/

#ifdef __cplusplus
}
#endif

#endif /* __MAIN_H */
'''

with open("main.h", "w") as f:
    f.write(main_h_content)

print("中断处理文件和头文件已创建")